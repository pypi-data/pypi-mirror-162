import { PK, ProgressModel, SubmitOptions } from 'state';
interface ErrorResponse {
    ok: false;
    fields: {
        [k: string]: string;
    };
    message: string;
    code: number;
}
declare type Response = {
    ok: true;
    pk: PK;
} | ErrorResponse;
declare type Progress = (p: ProgressModel | null) => void;
declare type TSubmit = (props: SubmitOptions, progress?: Progress) => Promise<Response>;
declare const Submit: TSubmit;
export { Submit as SubmitBraceForm };
//# sourceMappingURL=form.d.ts.map