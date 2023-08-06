let plugins = [
        {'info-source': {
            'sel':0
            }}
    ];
    function ClearInfoClass() {
        $('.info-source').removeClass('bg-light')
    }

    function ClearConfigInfoClass() {
        $('.config-info-source').removeClass('bg-light')
    }

    function HideDocumentation() {
        $('.help-view').hide()
    }

    function HideConfigs() {
        $('.plugin-config-set').hide()
    }

    function activatePluginsGui() {
        console.log('plugins template initialized');
        $('.info-source').click(function() {
            ClearInfoClass();
            ClearConfigInfoClass();
            HideDocumentation();
            HideConfigs();
            $(this).addClass('bg-light');
            let pluginName = $(this).data("name");
            $(`#${pluginName}-help`).show();
            $(`#${pluginName}-config-set`).show();
        });
        $('.config-info-source').click(function() {
            ClearInfoClass();
            ClearConfigInfoClass();
            HideDocumentation();
            $(this).addClass('bg-light');
            let pluginName = $(this).data("name");
            $(`#${pluginName}-help`).show();
            $(`#${pluginName}-config-set`).show();
        });

        $('.plugin-checkbox').change(function () {
            let el = $(this);
            let name = el.val();
            let check = el.prop('checked');
            console.log("Change: " + name + " to " + check);
            pluginsToConfig();
        });

        $('.plugin-param-checkbox').change(function(){pluginsToConfig();});
        $('.plugin-param-input').change(function(){pluginsToConfig();});
        pluginsToConfig();
    }

    function renderPythonConfiguration(plugins) {
        let resulting_html = "";

        for(let [i, plugin] of plugins.entries()) {

            let args_str = `'${plugin.name}'`;   // a string with arguments for .plugin(...) function call

            // Do we have plugin parameters?

                for(let parameter of plugin.parameters) {
                    let escaped_value = '';
                    if(parameter.type === 'string') {
                        escaped_value = `'${parameter.value}'`;     // Take string into quotes
                    }
                    else {
                        escaped_value = `${parameter.value}`;       // Other parameters are out for now
                    }
                    args_str += `, ${parameter.name}=${escaped_value}`
                }

            let api_calls_str = `.plugin(${args_str})`;
            if (i !== plugins.length - 1) {
                api_calls_str += ' \\';
            }
            resulting_html += `${api_calls_str}</br>`;
        }
        $('.v-pills-python code').html(resulting_html);
    }

    function pluginsToConfig() {
        let plugins = [];
        let plugins_by_name = {};

        $('.plugin-checkbox:checked').each(function() {
            let plugin = {'name': this.dataset.name, 'parameters': [], 'parameters_by_name': {}};
            plugins.push(plugin);
            plugins_by_name[plugin.name] = plugin;
        });

        // plugin-param-checkbox plugin-param-input


        let output = "";
        for(let plugin of plugins) {
            console.log(`Looking parameters for ${plugin}`);

            $(`input.plugin-param-checkbox[data-plugin=${plugin.name}]:checked`).each(function() {
                let full_name = this.dataset.name;


                let param_input = $(`input.plugin-param-input[data-name='${full_name}']`).first();
                console.log(param_input.val());
                //param_input.
                let parameter = {
                    'full_name': full_name,
                    'name': param_input.data('parname'),
                    'type': param_input.data('plugintype'),
                    'value': param_input.val()};

                plugin.parameters.push(parameter);
                plugin.parameters_by_name[parameter.full_name] = parameter;
                console.log('parameter');
                console.log(parameter);

                output += `${full_name}=${parameter.value}`;
            });


            output += plugin + " ";
        }

        renderPythonConfiguration(plugins);

        $('#config-help').text(output)
    }