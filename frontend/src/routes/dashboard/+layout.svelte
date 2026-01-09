<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		if (!auth.loading && !auth.isAuthenticated) {
			goto('/login');
		}
	});

	$effect(() => {
		if (!auth.loading && !auth.isAuthenticated) {
			goto('/login');
		}
	});
</script>

{#if auth.isAuthenticated}
	{@render children()}
{:else}
	<div class="flex items-center justify-center">
		<span class="text-muted-foreground">Redirecting to login...</span>
	</div>
{/if}
