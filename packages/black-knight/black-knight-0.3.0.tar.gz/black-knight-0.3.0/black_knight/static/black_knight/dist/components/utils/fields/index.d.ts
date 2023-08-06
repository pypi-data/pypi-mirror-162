import { FC } from 'react';
import { FieldModel } from 'state';
import { FieldProps } from './shared';
declare type TRenderField = FC<Omit<FieldProps<FieldModel>, 'change'>>;
declare const RenderField: TRenderField;
export { RenderField };
//# sourceMappingURL=index.d.ts.map