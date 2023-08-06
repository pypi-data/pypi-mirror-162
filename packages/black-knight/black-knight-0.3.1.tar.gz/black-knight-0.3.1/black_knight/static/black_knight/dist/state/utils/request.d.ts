import { AxiosRequestConfig } from 'axios';
interface ResponseOk {
    ok: true;
    data: any;
}
interface ResponseError {
    ok: false;
    message: string;
    code: number;
}
declare type Response = ResponseOk | ResponseError;
declare type TRequest = (config: AxiosRequestConfig<FormData | Object>) => Promise<Response>;
declare const REQUEST: TRequest;
export { REQUEST };
//# sourceMappingURL=request.d.ts.map