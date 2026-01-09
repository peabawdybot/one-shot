<script lang="ts">
	import { api } from '$lib/api/client';

	interface AdminUser {
		id: string;
		email: string;
		role: 'user' | 'admin';
		is_active: boolean;
		created_at: string;
		last_login_at: string | null;
		task_count: number;
	}

	let { users, onStatusChange }: { users: AdminUser[]; onStatusChange: () => void } = $props();
	let updatingId = $state<string | null>(null);

	async function toggleStatus(user: AdminUser) {
		if (user.role === 'admin') {
			alert('Cannot deactivate admin accounts from the UI');
			return;
		}

		const action = user.is_active ? 'deactivate' : 'activate';
		if (!confirm(`Are you sure you want to ${action} ${user.email}?`)) {
			return;
		}

		updatingId = user.id;
		const response = await api.patch(`/admin/users/${user.id}`, {
			is_active: !user.is_active,
		});

		if (response.error) {
			alert(response.error);
		} else {
			onStatusChange();
		}
		updatingId = null;
	}

	function formatDate(dateString: string | null): string {
		if (!dateString) return 'Never';
		return new Date(dateString).toLocaleDateString();
	}
</script>

<div class="overflow-x-auto rounded-lg border">
	<table class="w-full">
		<thead class="border-b bg-muted/50">
			<tr>
				<th class="px-4 py-3 text-left text-sm font-medium">Email</th>
				<th class="px-4 py-3 text-left text-sm font-medium">Role</th>
				<th class="px-4 py-3 text-left text-sm font-medium">Status</th>
				<th class="px-4 py-3 text-left text-sm font-medium">Tasks</th>
				<th class="px-4 py-3 text-left text-sm font-medium">Last Login</th>
				<th class="px-4 py-3 text-left text-sm font-medium">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each users as user (user.id)}
				<tr class="border-b last:border-b-0 hover:bg-muted/30">
					<td class="px-4 py-3 text-sm">{user.email}</td>
					<td class="px-4 py-3">
						<span
							class="rounded-full px-2 py-0.5 text-xs font-medium {user.role === 'admin'
								? 'bg-primary text-primary-foreground'
								: 'bg-secondary text-secondary-foreground'}"
						>
							{user.role}
						</span>
					</td>
					<td class="px-4 py-3">
						<span
							class="rounded-full px-2 py-0.5 text-xs font-medium {user.is_active
								? 'bg-green-100 text-green-800'
								: 'bg-red-100 text-red-800'}"
						>
							{user.is_active ? 'Active' : 'Inactive'}
						</span>
					</td>
					<td class="px-4 py-3 text-sm">{user.task_count}</td>
					<td class="px-4 py-3 text-sm text-muted-foreground">
						{formatDate(user.last_login_at)}
					</td>
					<td class="px-4 py-3">
						{#if user.role !== 'admin'}
							<button
								onclick={() => toggleStatus(user)}
								disabled={updatingId === user.id}
								class="rounded px-2 py-1 text-xs {user.is_active
									? 'text-destructive hover:bg-destructive/10'
									: 'text-green-600 hover:bg-green-50'} disabled:opacity-50"
							>
								{updatingId === user.id
									? '...'
									: user.is_active
										? 'Deactivate'
										: 'Activate'}
							</button>
						{:else}
							<span class="text-xs text-muted-foreground">—</span>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
