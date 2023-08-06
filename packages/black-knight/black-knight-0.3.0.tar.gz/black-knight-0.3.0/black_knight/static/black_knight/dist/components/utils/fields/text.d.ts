import { FC } from 'react';
import { CharBasedFieldsModel, JsonFieldModel, TextFieldModel } from 'state';
import { FieldProps } from './shared';
declare type TChar = FC<FieldProps<CharBasedFieldsModel>>;
declare const CharField: TChar;
declare type TText = FC<FieldProps<TextFieldModel>>;
declare const TextField: TText;
declare type TJson = FC<FieldProps<JsonFieldModel>>;
declare const JsonField: TJson;
export { CharField, TextField, JsonField };
//# sourceMappingURL=text.d.ts.map