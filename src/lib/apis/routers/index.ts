import { WEBUI_API_BASE_URL } from '$lib/constants';

export async function getRouters(token: string): Promise<any[]> {
    try {
        const response = await fetch(`${WEBUI_API_BASE_URL}/routers`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch routers');
        }

        const data = await response.json();
        return data.routers;
    } catch (error) {
        console.error('Error fetching routers:', error);
        throw error;
    }
}

export async function updateRouterSettings(token: string, routerId: string, settings: any): Promise<boolean> {
    try {
        const response = await fetch(`${WEBUI_API_BASE_URL}/routers/${routerId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        if (!response.ok) {
            throw new Error('Failed to update router settings');
        }

        return true;
    } catch (error) {
        console.error('Error updating router settings:', error);
        throw error;
    }
}