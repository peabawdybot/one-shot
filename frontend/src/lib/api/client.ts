import { browser } from '$app/environment';

const API_URL = browser ? (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api') : 'http://localhost:8000/api';

interface ApiResponse<T> {
	data?: T;
	error?: string;
	status: number;
}

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
	accessToken = token;
	if (browser && token) {
		localStorage.setItem('access_token', token);
	} else if (browser) {
		localStorage.removeItem('access_token');
	}
}

export function getAccessToken(): string | null {
	if (accessToken) return accessToken;
	if (browser) {
		accessToken = localStorage.getItem('access_token');
	}
	return accessToken;
}

async function request<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<ApiResponse<T>> {
	const token = getAccessToken();

	const headers: HeadersInit = {
		'Content-Type': 'application/json',
		...options.headers,
	};

	if (token) {
		(headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
	}

	try {
		const response = await fetch(`${API_URL}${endpoint}`, {
			...options,
			headers,
			credentials: 'include',
		});

		if (response.status === 204) {
			return { status: response.status };
		}

		const data = await response.json().catch(() => null);

		if (!response.ok) {
			return {
				error: data?.detail || 'An error occurred',
				status: response.status,
			};
		}

		return { data, status: response.status };
	} catch (error) {
		return {
			error: error instanceof Error ? error.message : 'Network error',
			status: 0,
		};
	}
}

export const api = {
	get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),

	post: <T>(endpoint: string, body?: unknown) =>
		request<T>(endpoint, {
			method: 'POST',
			body: body ? JSON.stringify(body) : undefined,
		}),

	put: <T>(endpoint: string, body?: unknown) =>
		request<T>(endpoint, {
			method: 'PUT',
			body: body ? JSON.stringify(body) : undefined,
		}),

	patch: <T>(endpoint: string, body?: unknown) =>
		request<T>(endpoint, {
			method: 'PATCH',
			body: body ? JSON.stringify(body) : undefined,
		}),

	delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
};
