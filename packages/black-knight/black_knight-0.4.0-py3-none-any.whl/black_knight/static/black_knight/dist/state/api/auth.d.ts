declare const Logout: () => Promise<void>;
interface LoginData {
    username: string;
    password: string;
}
declare const Login: (data: LoginData) => Promise<boolean>;
export { Logout, Login };
//# sourceMappingURL=auth.d.ts.map