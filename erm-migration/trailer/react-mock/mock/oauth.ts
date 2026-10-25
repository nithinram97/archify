export type PublicOauthClient = any;
export function createPublicOauthClient() { const f: any = async () => 'fake-token'; f.signIn = async () => {}; return f; }
