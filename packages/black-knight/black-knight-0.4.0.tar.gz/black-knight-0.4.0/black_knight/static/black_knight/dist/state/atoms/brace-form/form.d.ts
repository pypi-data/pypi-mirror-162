import { PK } from 'state';
import { FormErrors } from './store';
interface BraceFormArgs {
    app_label?: string;
    model_name?: string;
    pk?: PK;
}
declare const BraceFormAtom: import("jotai").WritableAtom<Promise<import("../../models/BraceForm").BraceFormModel | "loading" | "not-found">, BraceFormArgs, Promise<void>>;
export { BraceFormAtom, FormErrors as BFErrorsAtom };
//# sourceMappingURL=form.d.ts.map