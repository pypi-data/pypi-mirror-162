import { ErrorResponse, PK, ProgressModel, SubmitOptions, SuccessResponse } from 'state';
interface SRes extends SuccessResponse {
    pk: PK;
}
interface ERes extends ErrorResponse {
    fields?: {
        [k: string]: string;
    };
}
declare type Res = SRes | ERes;
declare type Progress = (p: ProgressModel | null) => void;
declare type TSubmit = (props: SubmitOptions, progress?: Progress) => Promise<Res>;
declare const Submit: TSubmit;
export { Submit as SubmitBraceForm };
//# sourceMappingURL=form.d.ts.map