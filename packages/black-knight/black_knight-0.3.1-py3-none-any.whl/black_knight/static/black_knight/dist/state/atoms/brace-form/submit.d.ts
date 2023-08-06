import { SubmitOptions } from 'state';
import { SubmitProgress } from './store';
declare type V = (string | Blob) | (string | Blob)[];
interface TArgs extends Omit<SubmitOptions, 'data'> {
    [k: `F_${string}`]: V;
}
declare const BFSData: import("jotai").WritableAtom<SubmitOptions, TArgs, void>;
export { BFSData, SubmitProgress as SubmitProgressAtom };
//# sourceMappingURL=submit.d.ts.map