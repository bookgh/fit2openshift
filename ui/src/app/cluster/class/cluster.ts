import {Node} from '../../node/node';
import {Execution} from '../../deploy/component/operater/execution';


export class Cluster {
  id: string;
  name: string;
  package: string;
  comment: string;
  template: string;
  date_created: string;
  current_task_id: string;
  state: string;
  node: Node[];
  configs: ExtraConfig[];
  current_execution: Execution;
}

export class ExtraConfig {
  key: string;
  value: any;
}
