import { SubmitOptions } from 'state';
declare type V = (string | Blob) | (string | Blob)[];
interface TArgs extends Omit<SubmitOptions, 'data'> {
    [k: `F_${string}`]: V;
}
declare const BFSData: import("jotai").WritableAtom<SubmitOptions, TArgs, void>;
export { BFSData };
//# sourceMappingURL=submit.d.ts.map