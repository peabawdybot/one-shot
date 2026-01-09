<script lang="ts">
	import '../app.css';
	import { auth } from '$lib/stores/auth';
	import { onMount } from 'svelte';
	import Navigation from '$lib/components/Navigation.svelte';

	let { children } = $props();

	onMount(() => {
		auth.init();
	});
</script>

<div class="min-h-screen bg-background">
	<Navigation />
	<main class="container mx-auto px-4 py-8">
		{#if auth.loading}
			<div class="flex items-center justify-center">
				<span class="text-muted-foreground">Loading...</span>
			</div>
		{:else}
			{@render children()}
		{/if}
	</main>
</div>
