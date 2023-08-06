import { SubmitOptions, PK } from 'state';
interface Err {
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
} | Err;
declare const Submit: (props: SubmitOptions) => Promise<Response>;
export { Submit as SubmitBraceForm };
//# sourceMappingURL=form.d.ts.map