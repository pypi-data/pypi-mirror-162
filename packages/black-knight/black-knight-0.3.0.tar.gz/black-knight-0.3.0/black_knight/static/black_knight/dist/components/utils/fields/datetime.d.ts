import { FC } from 'react';
import { DateFieldModel, DateTimeFieldModel, TimeFieldModel } from 'state';
import { FieldProps } from './shared';
declare type TDate = FC<FieldProps<DateFieldModel>>;
declare const DateField: TDate;
declare type TDateTime = FC<FieldProps<DateTimeFieldModel>>;
declare const DateTimeField: TDateTime;
declare type TTime = FC<FieldProps<TimeFieldModel>>;
declare const TimeField: TTime;
export { DateField, DateTimeField, TimeField };
//# sourceMappingURL=datetime.d.ts.map