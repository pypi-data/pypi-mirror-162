import { FC } from 'react';
import { BooleanFieldModel, DecimalFieldModel, FloatFieldModel, IntegerFieldModel } from 'state';
import { FieldProps } from './shared';
declare type TBoolean = FC<FieldProps<BooleanFieldModel>>;
declare const BooleanField: TBoolean;
declare type TInteger = FC<FieldProps<IntegerFieldModel>>;
declare const IntegerField: TInteger;
declare type TDecimal = FC<FieldProps<DecimalFieldModel>>;
declare const DecimalField: TDecimal;
declare type TFloat = FC<FieldProps<FloatFieldModel>>;
declare const FloatField: TFloat;
export { BooleanField, IntegerField, DecimalField, FloatField };
//# sourceMappingURL=number.d.ts.map