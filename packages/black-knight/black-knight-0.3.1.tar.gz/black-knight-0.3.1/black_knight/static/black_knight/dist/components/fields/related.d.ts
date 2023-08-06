import { FC } from 'react';
import { ForeignKeyFieldModel, ManyToManyFieldModel } from 'state';
import { FieldProps } from './shared';
declare type TForeignKey = FC<FieldProps<ForeignKeyFieldModel>>;
declare const ForeignKeyField: TForeignKey;
declare type TManyToMany = FC<FieldProps<ManyToManyFieldModel>>;
declare const ManyToManyField: TManyToMany;
export { ForeignKeyField, ManyToManyField };
//# sourceMappingURL=related.d.ts.map