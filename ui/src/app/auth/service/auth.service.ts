import {Injectable} from '@angular/core';
import {Package} from '../../package/package';
import {Auth} from '../class/auth';
import {OpenshiftCluster} from '../../cluster/class/openshift-cluster';

@Injectable({
  providedIn: 'root'
})
export class AuthService {


  constructor() {

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

  configAuth(auth: Auth) {
    const config = auth.config;
    auth.options.forEach(option => {
      if (option.type !== 'parent') {
        config[option.name] = option.value;
      } else {
        const obj = config[option.name] = {};
        option.children.forEach(children => {
          obj[children.name] = children.value;
        });
      }
    });
  }
}
