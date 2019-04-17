import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ClusterRole} from '../class/cluster-role';
import {Observable} from 'rxjs';
export const baseUrl = '/api/v1/clusters/{clusterName}/roles/{name}';

@Injectable({
  providedIn: 'root'
})
export class ClusterRoleService {

  constructor(private http: HttpClient) {
  }

  getClusterRole(cluster_name, name): Observable<ClusterRole> {
    return this.http.get<ClusterRole>(baseUrl.replace('{clusterName}', cluster_name).replace('{name}', name));
  }
}
