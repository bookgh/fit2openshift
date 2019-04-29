import {Component, OnInit} from '@angular/core';
import {Cluster} from '../cluster/class/cluster';
import {ActivatedRoute} from '@angular/router';
import {ClusterService} from '../cluster/service/cluster.service';
import {Package} from '../package/package';
import {Auth} from './class/auth';
import {PackageService} from '../package/package.service';
import {AuthService} from './service/auth.service';
import {OpenshiftCluster} from '../cluster/class/openshift-cluster';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent implements OnInit {

  currentCluster: Cluster;
  pkg: Package;
  auth: Auth;
  authTemplates: Auth[];

  constructor(private route: ActivatedRoute, private authService: AuthService,
              private clusterService: ClusterService, private packageService: PackageService) {
  }

  ngOnInit() {
    this.route.parent.data.subscribe(data => {
      this.currentCluster = data['cluster'];
      this.packageService.getPackage(this.currentCluster.package).subscribe(pkg => {
        this.pkg = pkg;
        this.authTemplates = this.authService.getAuthTemplatges(this.pkg);
      });
    });
  }

  setDefaultValue() {
    this.auth.options.forEach(op => {
      if (op.type !== 'parent') {
        op.value = op.default;
      } else {
        op.value = op.default;
        op.children.forEach(cop => {
          op.value[cop.name] = cop.default;
        });
      }
      this.auth.vars.forEach(v => {
        v.value = v.default;
      });
    });
  }

  onSubmit() {
    // this.authService.configAuth( );
  }


}
