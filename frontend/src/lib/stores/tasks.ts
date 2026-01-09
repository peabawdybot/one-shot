import { api } from '$lib/api/client';

interface Task {
	id: string;
	title: string;
	description: string | null;
	is_completed: boolean;
	created_at: string;
	updated_at: string;
}

interface TaskListResponse {
	tasks: Task[];
	total: number;
}

interface TaskCreate {
	title: string;
	description?: string;
}

interface TaskUpdate {
	title?: string;
	description?: string;
	is_completed?: boolean;
}

class TaskStore {
	tasks = $state<Task[]>([]);
	total = $state(0);
	loading = $state(false);
	error = $state<string | null>(null);
	filter = $state<'all' | 'active' | 'completed'>('all');

	filteredTasks = $derived(() => {
		if (this.filter === 'all') return this.tasks;
		if (this.filter === 'active') return this.tasks.filter((t) => !t.is_completed);
		return this.tasks.filter((t) => t.is_completed);
	});

	async fetchTasks(isCompleted?: boolean) {
		this.loading = true;
		this.error = null;

		const params = new URLSearchParams();
		if (isCompleted !== undefined) {
			params.set('is_completed', String(isCompleted));
		}

		const endpoint = `/tasks${params.toString() ? '?' + params.toString() : ''}`;
		const response = await api.get<TaskListResponse>(endpoint);

		if (response.error) {
			this.error = response.error;
		} else if (response.data) {
			this.tasks = response.data.tasks;
			this.total = response.data.total;
		}

		this.loading = false;
	}

	async createTask(data: TaskCreate): Promise<boolean> {
		this.error = null;
		const response = await api.post<Task>('/tasks', data);

		if (response.error) {
			this.error = response.error;
			return false;
		}

		if (response.data) {
			this.tasks = [response.data, ...this.tasks];
			this.total++;
			return true;
		}

		return false;
	}

	async updateTask(id: string, data: TaskUpdate): Promise<boolean> {
		this.error = null;
		const response = await api.put<Task>(`/tasks/${id}`, data);

		if (response.error) {
			this.error = response.error;
			return false;
		}

		if (response.data) {
			this.tasks = this.tasks.map((t) => (t.id === id ? response.data! : t));
			return true;
		}

		return false;
	}

	async deleteTask(id: string): Promise<boolean> {
		this.error = null;
		const response = await api.delete(`/tasks/${id}`);

		if (response.error) {
			this.error = response.error;
			return false;
		}

		this.tasks = this.tasks.filter((t) => t.id !== id);
		this.total--;
		return true;
	}

	async toggleComplete(id: string): Promise<boolean> {
		const task = this.tasks.find((t) => t.id === id);
		if (!task) return false;

		return this.updateTask(id, { is_completed: !task.is_completed });
	}

	setFilter(filter: 'all' | 'active' | 'completed') {
		this.filter = filter;
	}

	clearError() {
		this.error = null;
	}
}

export const taskStore = new TaskStore();
