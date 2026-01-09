<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		if (!auth.loading) {
			redirect();
		}
	});

	$effect(() => {
		if (!auth.loading) {
			redirect();
		}
	});

	function redirect() {
		if (auth.isAuthenticated) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	}
</script>

<div class="flex items-center justify-center">
	<span class="text-muted-foreground">Redirecting...</span>
</div>
