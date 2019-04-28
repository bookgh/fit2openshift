import {Injectable} from '@angular/core';
import {Package} from '../../package/package';
import {Auth} from '../class/auth';
import {OpenshiftCluster} from '../../cluster/class/openshift-cluster';
import {HttpClient} from '@angular/common/http';
import {OpenshiftClusterService} from '../../cluster/service/openshift-cluster.service';
import {ExtraConfig} from '../../cluster/class/cluster';
import {OperaterService} from '../../deploy/component/operater/operater.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {


  constructor(private http: HttpClient, private clusterService: OpenshiftClusterService, private optService: OperaterService) {

  }

  getAuthTemplatges(pa: Package) {
    return pa.meta.auth_templates;
  }

  getAuth(pa: Package, cluster: OpenshiftCluster) {
    const name = cluster.auth;
    let auth: Auth = new Auth();
    pa.meta.auth_templates.forEach(template => {
      if (template.name === name) {
        auth = template;
      }
    });
    return auth;
  }

  configAuth(auth: Auth, cluster: OpenshiftCluster) {
    const config = auth.config;
    auth.options.forEach(option => {
      config[option.name] = option.value;
    });
    const auth_list = [].push(config);
    const authConfig: ExtraConfig = new ExtraConfig();
    authConfig.key = 'openshift_master_identity_providers';
    authConfig.value = auth_list;
    const promises: Promise<{}>[] = [];
    const vars: ExtraConfig[] = [];
    auth.vars.forEach(_var => {
      const c: ExtraConfig = new ExtraConfig();
      c.key = _var.name;
      c.value = _var.value;
      vars.push(c);
    });
    promises.push(this.clusterService.configOpenshiftCluster(cluster.name, authConfig).toPromise());
    vars.forEach(c => {
      promises.push(this.clusterService.configOpenshiftCluster(cluster.name, c).toPromise());
    });
    Promise.all(promises).then(nil => {
      this.optService.executeOperate(cluster.name, 'config-auth').subscribe(data => {
        // 跳转term
        console.log(data);
      });
    });
  }
}
