import {Injectable} from '@angular/core';
import {Package} from '../../package/package';
import {Auth} from '../class/auth';
import {OpenshiftCluster} from '../../cluster/class/openshift-cluster';
import {HttpClient} from '@angular/common/http';
import {OpenshiftClusterService} from '../../cluster/service/openshift-cluster.service';
import {Cluster, ExtraConfig} from '../../cluster/class/cluster';
import {OperaterService} from '../../deploy/component/operater/operater.service';
import {Router} from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {


  constructor(private http: HttpClient, private clusterService: OpenshiftClusterService,
              private optService: OperaterService, private router: Router) {

  }

  getAuthTemplatges(pa: Package) {
    return pa.meta.auth_templates;
  }

  fullAuth(auth: Auth, cluster: Cluster) {
    this.clusterService.getOpenshiftClusterConfig(cluster.name, 'openshift_master_identity_providers').subscribe(data => {
      console.log(auth);
      const d = data.value[0];
      auth.options.forEach(option => {
        for (const key in d) {
          if (key === option.name) {
            option.value = d[key];
          }
        }
      });
      auth.vars.forEach(v => {
        this.clusterService.getOpenshiftClusterConfig(cluster.name, v.name).subscribe(data => {
          v.value = data.value;
        });
      });
    });
  }

  configAuth(auth: Auth, cluster: Cluster) {
    const config = auth.config;
    auth.options.forEach(option => {
      config[option.name] = option.value;
    });
    const auth_list = [];
    auth_list.push(config);
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
      this.clusterService.setOpenshiftClusterAuth(cluster.name, auth.name).subscribe(d => {
        this.optService.executeOperate(cluster.name, 'config-auth').subscribe(data => {
          this.router.navigate(['fit2openshift', 'cluster', cluster.name, 'deploy']);
        });
      });
    });
  }
}
