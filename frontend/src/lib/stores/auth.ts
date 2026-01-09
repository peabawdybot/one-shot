import { api, setAccessToken, getAccessToken } from '$lib/api/client';

interface User {
	id: string;
	email: string;
	role: 'user' | 'admin';
	is_active: boolean;
	created_at: string;
	last_login_at: string | null;
}

interface AuthResponse {
	access_token: string;
	token_type: string;
	user: User;
}

class AuthStore {
	user = $state<User | null>(null);
	loading = $state(true);
	error = $state<string | null>(null);

	isAuthenticated = $derived(this.user !== null);
	isAdmin = $derived(this.user?.role === 'admin');

	async init() {
		const token = getAccessToken();
		if (token) {
			await this.fetchCurrentUser();
		}
		this.loading = false;
	}

	async register(email: string, password: string): Promise<boolean> {
		this.error = null;
		const response = await api.post<AuthResponse>('/auth/register', { email, password });

		if (response.error) {
			this.error = response.error;
			return false;
		}

		if (response.data) {
			setAccessToken(response.data.access_token);
			this.user = response.data.user;
			return true;
		}

		return false;
	}

	async login(email: string, password: string): Promise<boolean> {
		this.error = null;
		const response = await api.post<AuthResponse>('/auth/login', { email, password });

		if (response.error) {
			this.error = response.error;
			return false;
		}

		if (response.data) {
			setAccessToken(response.data.access_token);
			this.user = response.data.user;
			return true;
		}

		return false;
	}

	async logout(): Promise<void> {
		await api.post('/auth/logout');
		setAccessToken(null);
		this.user = null;
	}

	async fetchCurrentUser(): Promise<void> {
		const response = await api.get<User>('/auth/me');
		if (response.data) {
			this.user = response.data;
		} else {
			setAccessToken(null);
			this.user = null;
		}
	}

	clearError() {
		this.error = null;
	}
}

export const auth = new AuthStore();
