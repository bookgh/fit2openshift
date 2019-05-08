import {Auth} from '../auth/class/auth';
import {Node} from '../node/node';


export class Package {
  id: string;
  name: string;
  meta: PackageMeta;
  date_created: string;
}

export class PackageMeta {
  name: string;
  version: string;
  resource: string;
  templates: Template[];
  auth_templates: Auth[];
  storage_templates: StorageTemplate[];
}

export class Config {
  name: string;
  alias: string;
  type: string;
  options: Option[];
  value: string;
  default: any;
  require: boolean;
  help_text: string;
}

export class Option {
  name: string;
  default: any;
  type: string;
  value: any;
  comment: string;
}

export class Role {
  name: string;
  meta: RoleMeta;
}

export class Requires {
  nodes_require: any[];
  volumes_require: Require[];
  device_require: Require[];
}

export class Require {
  name: string;
  verbose: string;
  minimal: number;
  excellent: number;
  unit: string;
  comment: string;
}

export class NodeVars {
  name: string;
  template: string;
  verbose: string;
  comment: string;
  type: string;
  options: any;
  placeholder: string;
  require: true;
}


export class RoleMeta {
  hidden: boolean;
  allow_os: Os[];
  requires: Requires;
  node_vars: NodeVars[];


}


export class Os {
  name: string;
  version: string[];
}

export class Template {
  name: string;
  roles: Role[];
  private_config: Config[];
  portals: Portal[];
  comment: string;
}

export class Portal {
  name: string;
  redirect: string;
}

export class StorageTemplate {
  name: string;
  roles: Role[];
  options: Option[];
  vars: StorageVar[];
}

export class StorageVar {
  name: string;
  value: any;
}

export class Storage {
  nodes: Node[] = [];
  vars: StorageVar[] = [];
}
