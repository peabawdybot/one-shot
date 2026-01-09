<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	let email = $state('');
	let password = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		loading = true;

		const success = await auth.login(email, password);

		if (success) {
			goto('/dashboard');
		}

		loading = false;
	}
</script>

<svelte:head>
	<title>Login - Task Manager</title>
</svelte:head>

<div class="mx-auto max-w-md">
	<div class="rounded-lg border bg-card p-8 shadow-sm">
		<h1 class="mb-6 text-2xl font-bold">Login</h1>

		{#if auth.error}
			<div class="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
				{auth.error}
			</div>
		{/if}

		<form onsubmit={handleSubmit} class="space-y-4">
			<div>
				<label for="email" class="mb-1 block text-sm font-medium">Email</label>
				<input
					type="email"
					id="email"
					name="email"
					bind:value={email}
					required
					class="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
					placeholder="you@example.com"
				/>
			</div>

			<div>
				<label for="password" class="mb-1 block text-sm font-medium">Password</label>
				<input
					type="password"
					id="password"
					name="password"
					bind:value={password}
					required
					class="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
					placeholder="••••••••"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full rounded-md bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
			>
				{loading ? 'Logging in...' : 'Login'}
			</button>
		</form>

		<p class="mt-4 text-center text-sm text-muted-foreground">
			Don't have an account?
			<a href="/register" class="text-primary hover:underline">Register</a>
		</p>
	</div>
</div>
