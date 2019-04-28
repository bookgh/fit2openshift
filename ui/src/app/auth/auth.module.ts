import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthComponent} from './auth.component';
import {CoreModule} from '../core/core.module';

@NgModule({
  declarations: [AuthComponent],
  imports: [
    CommonModule,
    CoreModule
  ]
})
export class AuthModule {
}
