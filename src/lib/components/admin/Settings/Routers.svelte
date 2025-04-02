<script lang="ts">
    import { onMount, getContext } from 'svelte';
    import type { Writable } from 'svelte/store';
    import { toast } from 'svelte-sonner';
    import { config } from '$lib/stores';
    import { getRouters, updateRouterSettings } from '$lib/apis/routers';

    import type { i18n as i18nType } from 'i18next';
    const i18n: Writable<i18nType> = getContext('i18n');

    import Spinner from '$lib/components/common/Spinner.svelte';
    
    export let saveHandler: Function;

    interface RouterSetting {
        enabled: boolean;
        classifier: string;
        model: string;
        n: number;
        threshold: number;
    }

    interface Router {
        id: string;
        name: string;
        settings: RouterSetting;
    }

    let routers: Router[] = [];
    let loading = true;
    let modelsSettings: RouterSetting | null = null;
    let toolsSettings: RouterSetting | null = null;
    let guardrailsSettings: RouterSetting | null = null;
    
    // Track UI state based on enabled settings
    $: showModelsSettings = modelsSettings?.enabled || false;
    $: showToolsSettings = toolsSettings?.enabled || false;
    $: showGuardrailsSettings = guardrailsSettings?.enabled || false;

    // Toggle functions that update the enabled state in settings objects
    const toggleModelsEnabled = () => {
        if (modelsSettings) {
            modelsSettings.enabled = !modelsSettings.enabled;
        }
    };

    const toggleToolsEnabled = () => {
        if (toolsSettings) {
            toolsSettings.enabled = !toolsSettings.enabled;
        }
    };

    const toggleGuardrailsEnabled = () => {
        if (guardrailsSettings) {
            guardrailsSettings.enabled = !guardrailsSettings.enabled;
        }
    };

    const updateHandler = async () => {
        try {
            let success = true;
            
            // Update each router individually
            if (modelsSettings) {
                console.log('Updating modelsSettings:', modelsSettings);
                const res = await updateRouterSettings(localStorage.token, "1", modelsSettings);
                console.log('Model router update response:', res);
                if (!res) success = false;
            }
            if (toolsSettings) {
                console.log('Updating toolsSettings:', toolsSettings);
                const res = await updateRouterSettings(localStorage.token, "2", toolsSettings);
                console.log('Tool router update response:', res);
                if (!res) success = false;
            }
            if (guardrailsSettings) {
                console.log('Updating guardrailsSettings:', guardrailsSettings);
                const res = await updateRouterSettings(localStorage.token, "3", guardrailsSettings);
                console.log('Guardrail router update response:', res);
                if (!res) success = false;
            }

            if (success) {
                toast.success($i18n.t('Router settings updated successfully'));
                await setRouters();
                saveHandler();
            }
        } catch (error) {
            console.error('Error updating router settings:', error);
            toast.error(`${error}`);
        }
    };

    const setRouters = async () => {
        try {
            loading = true;
            const routersData = await getRouters(localStorage.token);
            console.log('Fetched routers data:', routersData);
            if (routersData && Array.isArray(routersData)) {
                routers = routersData;
                routersData.forEach((router: Router) => {
                    switch (router.name) {
                        case "Model Router":
                            modelsSettings = router.settings;
                            break;
                        case "Tool Router":
                            toolsSettings = router.settings;
                            break;
                        case "Guardrail Router":
                            guardrailsSettings = router.settings;
                            break;
                    }
                });
            }
        } catch (error) {
            console.error('Error fetching routers:', error);
            toast.error($i18n.t('Failed to load routers'));
        } finally {
            loading = false;
        }
    };

    onMount(async () => {
        await setRouters();
    });
</script>

<form
    class="flex flex-col h-full justify-between space-y-6 rounded-lg shadow-lg"
    on:submit|preventDefault={async () => {
        updateHandler();
    }}
>
    <div class="overflow-y-scroll scrollbar-hidden h-full rounded-lg">
        {#if loading}
            <div class="flex justify-center items-center h-32">
                <Spinner size="md" />
            </div>
        {:else}
            <div class="flex w-full">
                <div class="mb-2.5 text-base font-medium">
                    {$i18n.t('Manage Routers')}
                </div>
            </div>
            <div class="space-y-6">
                {#if modelsSettings !== null}
                <div class="sub-section p-4 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-850/20 pb-4">
                    <div class="flex justify-between ">
                        <h3 class="mb-1 text-sm font-medium">{$i18n.t('Models Router Settings')}</h3>
                        <button 
                            data-state={modelsSettings.enabled ? "checked" : "unchecked"} 
                            type="button" 
                            role="switch" 
                            aria-checked={modelsSettings.enabled} 
                            class="flex h-5 min-h-5 w-9 shrink-0 cursor-pointer items-center rounded-full px-[3px] mx-[1px] transition bg-gray-200 dark:bg-transparent outline outline-1 outline-gray-100 dark:outline-gray-800"
                            on:click={toggleModelsEnabled}
                        >
                            <span 
                                class="pointer-events-none block size-4 shrink-0 rounded-full bg-white transition-transform data-[state=checked]:translate-x-3.5 data-[state=unchecked]:translate-x-0 data-[state=unchecked]:shadow-mini" 
                                data-state={modelsSettings.enabled ? "checked" : "unchecked"}
                            ></span>
                        </button>
                    </div>
                    <p class="mt-2 mb-1 text-xs text-gray-400 dark:text-gray-500 max-w-[90rem]">{$i18n.t(`
                    This model router is used to automatically classify the prompt and select the best model to generate the completion.
                    The model is then selected if the domain of the prompt matches the domain of the model or if the model has a high
                    completion probability for the prompt. The model is selected based on the n most probable completions and the threshold.
                    `)}</p>
                    {#if modelsSettings.enabled}
                    <div class="flex flex-col space-y-4 mt-4">
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('Model')}</label>
                            <input
                                type="text"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={modelsSettings.model}
                                placeholder={$i18n.t('Model')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('n')}</label>
                            <input
                                type="number"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={modelsSettings.n}
                                placeholder={$i18n.t('n')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('threshold')}</label>
                            <input
                                type="number"
                                step="0.01"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={modelsSettings.threshold}
                                placeholder={$i18n.t('threshold')}
                            />
                        </div>
                    </div>
                    {/if}
                </div>
                {/if}

                {#if toolsSettings !== null}
                <div class="sub-section p-4 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-850/20 pb-4">
                    <div class="flex justify-between items-center">
                        <h3 class="mb-1 text-sm font-medium">{$i18n.t('Tool Invocation Settings')}</h3>
                        <button 
                            data-state={toolsSettings.enabled ? "checked" : "unchecked"} 
                            type="button" 
                            role="switch" 
                            aria-checked={toolsSettings.enabled} 
                            class="flex h-5 min-h-5 w-9 shrink-0 cursor-pointer items-center rounded-full px-[3px] mx-[1px] transition bg-gray-200 dark:bg-transparent outline outline-1 outline-gray-100 dark:outline-gray-800"
                            on:click={toggleToolsEnabled}
                        >
                            <span 
                                class="pointer-events-none block size-4 shrink-0 rounded-full bg-white transition-transform data-[state=checked]:translate-x-3.5 data-[state=unchecked]:translate-x-0 data-[state=unchecked]:shadow-mini" 
                                data-state={toolsSettings.enabled ? "checked" : "unchecked"}
                            ></span>
                        </button>
                    </div>
                    <p class="mt-2 mb-1 text-xs text-gray-400 dark:text-gray-500 max-w-[90rem]">{$i18n.t(`
                    The tool router is used to automatically classify the prompt and enable the best tool to susccessfully complete the prompt.
                    `)}</p>
                    {#if toolsSettings.enabled}
                    <div class="flex flex-col space-y-4 mt-4">
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('Model')}</label>
                            <input
                                type="text"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={toolsSettings.model}
                                placeholder={$i18n.t('Model')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('n')}</label>
                            <input
                                type="number"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={toolsSettings.n}
                                placeholder={$i18n.t('n')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('threshold')}</label>
                            <input
                                type="number"
                                step="0.01"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={toolsSettings.threshold}
                                placeholder={$i18n.t('threshold')}
                            />
                        </div>
                    </div>
                    {/if}
                </div>
                {/if}

                {#if guardrailsSettings !== null}
                <div class="sub-section p-4 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-850/20 pb-4">
                    <div class="flex justify-between items-center">
                        <h3 class="mb-1 text-sm font-medium">{$i18n.t('Security Guardrails Settings')}</h3>
                        <button 
                            data-state={guardrailsSettings.enabled ? "checked" : "unchecked"} 
                            type="button" 
                            role="switch" 
                            aria-checked={guardrailsSettings.enabled} 
                            class="flex h-5 min-h-5 w-9 shrink-0 cursor-pointer items-center rounded-full px-[3px] mx-[1px] transition bg-gray-200 dark:bg-transparent outline outline-1 outline-gray-100 dark:outline-gray-800"
                            on:click={toggleGuardrailsEnabled}
                        >
                            <span 
                                class="pointer-events-none block size-4 shrink-0 rounded-full bg-white transition-transform data-[state=checked]:translate-x-3.5 data-[state=unchecked]:translate-x-0 data-[state=unchecked]:shadow-mini" 
                                data-state={guardrailsSettings.enabled ? "checked" : "unchecked"}
                            ></span>
                        </button>
                    </div>
                    <p class="mt-2 mb-1 text-xs text-gray-400 dark:text-gray-500 max-w-[90rem]">{$i18n.t(`
                    The guardrail router is used to detect and prevent adversarial prompts from being sent to the model or harmful content from being generated.
                    `)}</p>
                    {#if guardrailsSettings.enabled}
                    <div class="flex flex-col space-y-4 mt-4">
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('Model')}</label>
                            <input
                                type="text"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={guardrailsSettings.model}
                                placeholder={$i18n.t('Model')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('n')}</label>
                            <input
                                type="number"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={guardrailsSettings.n}
                                placeholder={$i18n.t('n')}
                            />
                        </div>
                        <div class="flex flex-col space-y-2">
                            <label class="mb-1.5 text-sm font-medium">{$i18n.t('threshold')}</label>
                            <input
                                type="number"
                                step="0.01"
                                class="w-full rounded-lg px-3 py-2 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden h-full"
                                bind:value={guardrailsSettings.threshold}
                                placeholder={$i18n.t('threshold')}
                            />
                        </div>
                    </div>
                    {/if}
                </div>
                {/if}
            </div>
        {/if}
    </div>
    <div class="flex justify-end mt-6">
        <button
            type="submit"
            class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
        >
            {$i18n.t('Save')}
        </button>
    </div>
</form>