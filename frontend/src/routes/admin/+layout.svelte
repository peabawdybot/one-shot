<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		checkAdmin();
	});

	$effect(() => {
		if (!auth.loading) {
			checkAdmin();
		}
	});

	function checkAdmin() {
		if (!auth.loading) {
			if (!auth.isAuthenticated) {
				goto('/login');
			} else if (!auth.isAdmin) {
				goto('/dashboard');
			}
		}
	}
</script>

{#if auth.isAdmin}
	{@render children()}
{:else if auth.loading}
	<div class="flex items-center justify-center">
		<span class="text-muted-foreground">Loading...</span>
	</div>
{:else}
	<div class="flex items-center justify-center">
		<span class="text-muted-foreground">Access denied. Redirecting...</span>
	</div>
{/if}
