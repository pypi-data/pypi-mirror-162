export * from './Admin';
export * from './BraceForm';
export * from './BraceList';
export * from './Fields';
export * from './Log';
export * from './User';
export type { ProgressModel };
export type { PK, TLoading, TValue, TBaseValue, TypedValues };
export type { VImage, VDate, VDateTime, VTime, VLink, VForeignKey, VFile, VManyToMany, };
interface ProgressModel {
    done: boolean;
    percentage: number;
    total: number;
    loaded: number;
}
declare type PK = string | number;
declare type TLoading = ['loading', string];
declare type VImage = ['image', string | null];
declare type VFile = ['file', string | null];
declare type VDate = ['date', string];
declare type VDateTime = ['datetime', string];
declare type VTime = ['time', string];
declare type VLink = ['link', string];
declare type VForeignKey = ['foreign_key', PK, string];
declare type VManyToMany = ['many_to_many', PK[]];
declare type TBaseValue = string | number | boolean | null;
declare type TypedValues = VImage | VDate | VTime | VDateTime | VLink | VForeignKey | VManyToMany | VFile;
declare type TValue = TBaseValue | TypedValues;
//# sourceMappingURL=index.d.ts.map