import { FC, HTMLAttributes, ReactNode } from 'react';
interface IntersectProps extends HTMLAttributes<HTMLDivElement> {
    children: ReactNode;
    options?: IntersectionObserverInit;
}
declare const Intersect: FC<IntersectProps>;
export { Intersect };
//# sourceMappingURL=Intersect.d.ts.map