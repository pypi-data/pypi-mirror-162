import { FC } from 'react';
import { FileFieldModel, FilePathFieldModel, ImageFieldModel } from 'state';
import { FieldProps } from './shared';
declare type TImage = FC<FieldProps<ImageFieldModel>>;
declare const ImageField: TImage;
declare type TFile = FC<FieldProps<FileFieldModel>>;
declare const FileField: TFile;
declare type TFilePath = FC<FieldProps<FilePathFieldModel>>;
declare const FilePathField: TFilePath;
export { ImageField, FileField, FilePathField };
//# sourceMappingURL=files.d.ts.map