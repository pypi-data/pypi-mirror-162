import { HTMLAttributes, ReactNode } from 'react';
declare type ChaneValue = (string | Blob) | (string | Blob)[];
interface FieldProps<TF> extends HTMLAttributes<HTMLElement> {
    change: (v: ChaneValue) => void;
    field: TF;
}
interface SelectProps<choice> extends HTMLAttributes<HTMLSelectElement> {
    choices: choice[];
    get_label: (c: choice, i: number) => ReactNode;
    get_value: (c: choice, i: number) => string | number;
    multiple?: boolean;
    get_selected?: (c: choice, i: number) => boolean;
}
declare function ChoicesField<choice>(props: SelectProps<choice>): JSX.Element;
export { FieldProps, ChoicesField };
//# sourceMappingURL=shared.d.ts.map