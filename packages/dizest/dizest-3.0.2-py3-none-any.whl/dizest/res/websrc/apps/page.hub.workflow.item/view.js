let wiz_controller = async ($sce, $scope, $timeout) => {
    let _$timeout = $timeout;
    $timeout = (timestamp) => new Promise((resolve) => _$timeout(resolve, timestamp));

    let ansi_up = new AnsiUp();

    let alert = async (message) => {
        await wiz.connect("modal.message")
            .data({
                title: "Alert",
                message: message,
                btn_action: "Close",
                btn_class: "btn-primary"
            })
            .event("modal-show");
    }

    const toBase64 = file => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });

    let DEFAULT_QUERY = {
        page: 1,
        dump: 40,
        text: ''
    };

    $scope.apps = {};
    $scope.apps.list = [];
    $scope.apps.loading = false;
    $scope.apps.tab = 'installed';

    $scope.apps.lastpage = 0;
    $scope.apps.query = angular.copy(DEFAULT_QUERY);

    $scope.apps.pagination = async () => {
        let lastpage = $scope.apps.lastpage * 1;
        let startpage = Math.floor(($scope.apps.query.page - 1) / 10) * 10 + 1;
        $scope.apps.pages = [];
        for (var i = 0; i < 10; i++) {
            if (startpage + i > lastpage) break;
            $scope.apps.pages.push(startpage + i);
        }
        await $timeout();
    }

    $scope.apps.load = {};
    $scope.apps.load.current = async (init) => {
        if (init) {
            $scope.apps.query.page = 1;
        }
        if ($scope.apps.tab == 'private') {
            await $scope.apps.load.private();
        } else {
            await $scope.apps.load.installed();
        }
    }

    $scope.apps.load.page = async (page) => {
        if (page < 1) {
            toastr.error('첫 페이지 입니다');
            return;
        }
        if (page > $scope.apps.lastpage) {
            toastr.error('마지막 페이지 입니다');
            return;
        }

        if ($scope.apps.query.page == page) {
            return;
        }

        $scope.apps.query.page = page;
        await $scope.apps.load.current();
    }

    $scope.sortableOptions = {
        stop: async () => {
            try {
                for (let i = 0; i < $scope.workflow.floworder.length; i++) {
                    let flow = $scope.workflow.floworder[i];
                    $scope.workflow.data.flow[flow.id].order = i + 1;
                }
            } catch (e) {
            }
        }
    };

    $scope.moveup = async (i, list) => {
        tmp = list[i];
        list.splice(i, 1);
        list.splice(i - 1, 0, tmp);
        await $timeout();

        try {
            for (let i = 0; i < $scope.workflow.floworder.length; i++) {
                let flow = $scope.workflow.floworder[i];
                $scope.workflow.data.flow[flow.id].order = i + 1;
            }
        } catch (e) {
        }
    }

    $scope.movedown = async (i, list) => {
        tmp = list[i];
        list.splice(i, 1);
        list.splice(i + 1, 0, tmp);
        await $timeout();

        try {
            for (let i = 0; i < $scope.workflow.floworder.length; i++) {
                let flow = $scope.workflow.floworder[i];
                $scope.workflow.data.flow[flow.id].order = i + 1;
            }
        } catch (e) {
        }
    }

    $scope.apps.load.installed = async () => {
        await $scope.workflow.update();

        $scope.workflow.floworder = [];
        for (let key in $scope.workflow.data.flow) {
            if (!$scope.workflow.data.flow[key].order) {
                $scope.workflow.data.flow[key].order = 999999;
            }

            if (!$scope.apps.query.text) {
                $scope.workflow.floworder.push($scope.workflow.data.flow[key]);
            }

            if ($scope.apps.query.text && $scope.workflow.data.flow[key].name.toLowerCase().includes($scope.apps.query.text.toLowerCase())) {
                $scope.workflow.floworder.push($scope.workflow.data.flow[key]);
            }
        }

        $scope.workflow.floworder.sort((a, b) => {
            return a.order - b.order;
        });

        $scope.apps.tab = 'installed';
        $scope.apps.loading = true;
        await $scope.apps.pagination();
        await $timeout();
    }

    $scope.apps.load.private = async (init) => {
        if (init) {
            $scope.apps.query = angular.copy(DEFAULT_QUERY);
        }

        let q = angular.copy($scope.apps.query);
        let res = await wiz.API.async("myapps", q);
        $scope.apps.list = res.data.result;
        $scope.apps.lastpage = res.data.lastpage;
        $scope.apps.tab = 'private';
        $scope.apps.loading = true;

        await $scope.apps.pagination();
        await $timeout();
    }

    // workflow
    $scope.workflow = {};
    $scope.workflow.loaded = false;

    $scope.workflow.data = {
        title: '',
        version: '',
        visibility: 'private',
        updatepolicy: 'auto',
        logo: '',
        featured: '',
        description: '',
        flow: {}
    };

    if (wiz.data.workflow) {
        $scope.workflow.data = wiz.data.workflow;
        $scope.workflow.url = wiz.API.url("download/" + wiz.data.workflow.id);
    }

    $scope.workflow.active_flow = async (item) => {
        $scope.workflow.active_flow_id = item;
        await $timeout();
    }

    $scope.workflow.delete = async () => {
        let data = angular.copy($scope.workflow.data);
        let res = await wiz.connect("modal.message")
            .data({
                title: "Delete Workflow",
                message: "Are you sure delete `" + data.title + "` Workflow?",
                btn_close: 'Close',
                btn_action: "Delete",
                btn_class: "btn-danger"
            })
            .event("modal-show");

        if (!res) {
            return;
        }

        await wiz.API.async("delete", { data: JSON.stringify(data) });
        location.href = "/hub/workflow";
    }

    $scope.workflow.update = async () => {
        let data = angular.copy($scope.workflow.data);
        let flows = editor.export().drawflow.Home.data;
        let apps = {};
        for (let flow_id in flows) {
            delete flows[flow_id].html;
            let app_id = flow_id.split("-")[0];
            apps[app_id] = await appLoader(app_id, false);
            flows[flow_id]['app_id'] = app_id;
            let outputs = {};
            for (let key in flows[flow_id].outputs) {
                let item = flows[flow_id].outputs[key];
                for (let i = 0; i < item.connections.length; i++)
                    item.connections[i].output = item.connections[i].output.substring(6);
                outputs[key.substring(7)] = item
            }
            flows[flow_id].outputs = outputs;

            let inputs = {};
            for (let key in flows[flow_id].inputs) {
                let item = flows[flow_id].inputs[key];
                for (let i = 0; i < item.connections.length; i++)
                    item.connections[i].input = item.connections[i].input.substring(7);
                inputs[key.substring(6)] = item
            }
            flows[flow_id].inputs = inputs;
            if (data.flow[flow_id])
                flows[flow_id].order = data.flow[flow_id].order;
        }

        data.apps = apps;
        data.flow = flows;
        data.description = $scope.workflow.desc_editor.data.get();
        $scope.workflow.data = data;
        await $timeout();
        return data;
    }

    $scope.workflow.save = async (background) => {
        let data = await $scope.workflow.update();

        if (!data.title || data.title.length == 0) {
            await alert("Workflow title is not filled.");
            $('#offcanvas-workflow-info').offcanvas('show');
            return;
        }

        if (!data.version || data.version.length == 0) {
            await alert("Workflow Version is not filled.");
            $('#offcanvas-workflow-info').offcanvas('show');
            return;
        }

        let res = null;
        if (data.id) {
            res = await wiz.API.async("update", { data: JSON.stringify(data) });
            if (res.code == 200 && !background)
                toastr.success("Saved");
            else if (res.code != 200)
                toastr.error("Error");
        } else {
            res = await wiz.API.async("create", { data: JSON.stringify(data) });
            if (res.code == 200) {
                let wpid = res.data;
                location.href = "/hub/workflow/item/" + wpid;
            } else {
                toastr.error("Error");
            }
        }

        await $scope.apps.load.current();
    }

    $scope.workflow.tab = async () => {
        $scope.workflow.current = 'info';
        await $timeout();
    }

    $scope.workflow.uploader = {};
    $scope.workflow.uploader.logo = async () => {
        $('#file-logo').click();
        $('#file-logo').change(async () => {
            let file = document.querySelector('#file-logo').files[0];
            file = await toBase64(file);
            $('#file-logo').val(null);
            if (file.length > 1024 * 100) {
                await alert("file size under 100kb");
                return;
            }
            $scope.workflow.data.logo = file;
            await $timeout();
        });
    }

    $scope.workflow.uploader.featured = async () => {
        $('#file-featured').click();
        $('#file-featured').change(async () => {
            let file = document.querySelector('#file-featured').files[0];
            file = await toBase64(file);
            $('#file-featured').val(null);
            if (file.length > 1024 * 100) {
                await alert("file size under 100kb");
                return;
            }
            $scope.workflow.data.featured = file;
            await $timeout();
        });
    }

    // init

    // ckeditor
    const EDITOR_ID = '#description-editor';
    $scope.workflow.desc_editor = await ClassicEditor.create(document.querySelector(EDITOR_ID), {
        language: 'en',
        toolbar: {
            items: 'heading | blockQuote bold italic strikethrough underline | bulletedList numberedList | outdent indent | imageUpload link code codeBlock'.split(' '),
            shouldNotGroupWhenFull: true
        },
        removePlugins: ["MediaEmbedToolbar"]
    });

    if ($scope.workflow.data.description)
        $scope.workflow.desc_editor.data.set($scope.workflow.data.description);

    if (!$scope.workflow.data.id) {
        $('#offcanvas-workflow-info').offcanvas('show');
    }

    // app
    $scope.app = {};
    $scope.app.data = null;

    $scope.app.description = await ClassicEditor.create(document.querySelector('#app-description'), {
        language: 'en',
        toolbar: {
            items: 'heading | blockQuote bold italic strikethrough underline | bulletedList numberedList | outdent indent | imageUpload link code codeBlock'.split(' '),
            shouldNotGroupWhenFull: true
        },
        removePlugins: ["MediaEmbedToolbar"]
    });

    $scope.app.description.enableReadOnlyMode('app-description');

    // drawflow
    let editor = $scope.drawflow = null;

    let create_html = (nodeid, item) => {
        let container = $("<div class='card-header'></div>");
        container.append('<div class="avatar-area avatar-area-sm mr-2"><div class="avatar-container"><span class="avatar" style="background-image: url(' + item.logo + ')"></span></div></div>')
        container.append('<h2 class="card-title" style="line-height: 1;">' + item.title + '<br/><small class="text-white" style="font-size: 10px; font-weight: 100; font-family: \'MAIN-R\'">' + item.version + '</small></h2>');
        container.append('<div class="ml-auto"></div>');
        container.append('<button class="btn btn-sm btn-white" onclick="removeNode(\'' + nodeid + '\')"><i class="fa-solid fa-xmark"></i></button>');
        let html = container.prop('outerHTML');

        let actions = $('<div class="card-body actions d-flex p-0"></div>');
        actions.append('<span class="finish-indicator status-indicator"></span>')
        actions.append('<span class="pending-indicator status-indicator status-yellow status-indicator-animated"><span class="status-indicator-circle"><span class="status-indicator-circle"></span><span class="status-indicator-circle"></span><span class="status-indicator-circle"></span></span>')
        if (item.mode == 'ui') actions.append('<div class="action-btn" onclick="appDisplay(\'' + nodeid + '\')"><i class="fa-solid fa-display"></i></div>');
        actions.append('<div class="action-btn" onclick="appInfo(\'' + item.id + '\')"><i class="fa-solid fa-info"></i></div>');
        actions.append('<div class="action-btn" onclick="appCode(\'' + nodeid + '\')"><i class="fa-solid fa-code"></i></div>');
        actions.append('<div class="action-btn action-btn-play" onclick="appRun(\'' + nodeid + '\')"><i class="fa-solid fa-play"></i></div>');
        actions.append('<div class="action-btn action-btn-stop" onclick="appStop(\'' + nodeid + '\')"><i class="fa-solid fa-stop"></i></div>');
        html = html + actions.prop('outerHTML');

        html = html + '<div class="progress progress-sm" style="border-radius: 0;"><div class="progress-bar bg-primary progress-bar-indeterminate"></div></div>';

        let value_container = $("<div class='card-body value-container p-0'></div>");
        let value_counter = 0;
        value_container.append('<div class="value-header">Variables</div>');
        for (let i = 0; i < item.inputs.length; i++) {
            let value = item.inputs[i];
            if (value.type == 'variable') {
                let variable_name = value.name;
                let wrapper = $("<div class='value-wrapper'></div>");
                wrapper.append('<div class="value-title">' + variable_name + '</div>');

                if (value.inputtype == 'number') {
                    wrapper.append('<div class="value-data"><input type="number" class="form-control form-control-sm" placeholder="' + value.description + '" df-' + variable_name + '/></div>');
                } else if (value.inputtype == 'date') {
                    wrapper.append('<div class="value-data"><input type="date" class="form-control form-control-sm" placeholder="' + value.description + '" df-' + variable_name + '/></div>');
                } else if (value.inputtype == 'memo') {
                    wrapper.append('<div class="value-data"><textarea rows=5 class="form-control form-control-sm" placeholder="' + value.description + '" df-' + variable_name + '></textarea></div>');
                } else if (value.inputtype == 'list') {
                    let vals = value.description;
                    vals = vals.replace(/\n/gim, "").split(",");
                    let opts = "";
                    for (let j = 0; j < vals.length; j++) {
                        vals[j] = vals[j].split(":");
                        let listkey = vals[j][0].trim();
                        let listval = listkey;
                        if (vals[j].length > 1) {
                            listval = vals[j][1].trim();
                        }
                        opts = opts + "<option value='" + listval + "'>" + listkey + "</option>"
                    }

                    opts = '<div class="value-data"><select class="form-select form-select-sm" df-' + variable_name + '>' + opts + "</select></div>";
                    wrapper.append(opts);
                } else {
                    wrapper.append('<div class="value-data"><input class="form-control form-control-sm" placeholder="' + value.description + '" df-' + variable_name + '/></div>');
                }


                value_container.append(wrapper);
                value_counter++;
            }
        }

        if (value_counter > 0)
            html = html + value_container.prop('outerHTML');

        return html;
    }

    let mobile_item_selec = '';
    let mobile_last_move = null;

    let apps = {};
    if (wiz.data.workflow && wiz.data.workflow.apps) {
        apps = wiz.data.workflow.apps;
    }

    let appLoader = async (app_id, update) => {
        if (update === false)
            if (apps[app_id])
                return angular.copy(apps[app_id]);
        if ($scope.workflow.data.updatepolicy != 'auto')
            if (!update && apps[app_id]) return angular.copy(apps[app_id]);
        let res = await wiz.API.async("get", { id: app_id, isfull: true });
        if (res.code != 200) return null;
        apps[app_id] = res.data;
        return angular.copy(apps[app_id]);
    }

    $scope.app.loader = async (app_id) => {
        let app = await appLoader(app_id, true);
        $scope.app.data = app;
        await $timeout();
    }

    window.removeNode = (nodeid) => {
        editor.removeNodeId('node-' + nodeid);
    }

    $scope.workflow.status = {};

    let socket = wiz.socket.get();
    if ($scope.workflow.data.id) {
        let wpid = $scope.workflow.data.id;
        $scope.socket = {};
        $scope.socket.running_status = {};
        $scope.socket.log = "";
        $scope.socket.clear = async () => {
            $scope.socket.log = "";
            await $timeout();
        }

        socket.on("log", async (data) => {
            data = data.replace(/ /gim, "__SEASONWIZPADDING__");
            data = ansi_up.ansi_to_html(data).replace(/\n/gim, '<br>').replace(/__SEASONWIZPADDING__/gim, '&nbsp;');
            $scope.socket.log = $scope.socket.log + data;
            await $timeout();
            let element = $('.dizest-debug-messages')[0];
            if (!element) return;
            element.scrollTop = element.scrollHeight - element.clientHeight;
        });

        socket.on("connect", function (data) {
            socket.emit("join", wpid);
        });

        socket.on("wpstatus", async (data) => {
            $scope.workflow.running = data;
            await $timeout();
        });

        socket.on("status", async (data) => {
            $scope.socket.running_status = data;
            let node_id = '#node-' + data.flow_id;
            $(node_id + " .error-message").remove();
            if (data.code == 2)
                $(node_id).append('<div class="error-message p-3 pt-2 pb-2 bg-red-lt">' + data.message + '</div>')
            if (data.code == 1)
                $(node_id).append('<div class="error-message p-3 pt-2 pb-2 bg-red-lt">Run the previous app first</div>')
            $scope.workflow.status[data.flow_id] = data;
            $('.flow-' + data.flow_id + ' .finish-indicator').text('[' + data.index + ']');
            await $timeout();
        });

        socket.on("stop", async () => {
            $scope.socket.running_status = {};
            $scope.workflow.status = {};
            $("#drawflow .error-message").remove();
            await $timeout();
        });
    }

    $scope.workflow.run = async () => {
        $scope.workflow.status = {};
        await $scope.workflow.save(true);
        let floworder = [];

        for (let key in $scope.workflow.data.flow) {
            if (!$scope.workflow.data.flow[key].order) {
                $scope.workflow.data.flow[key].order = 99999;
            }
            floworder.push($scope.workflow.data.flow[key]);
        }

        floworder.sort((a, b) => {
            return a.order - b.order;
        });

        await wiz.API.async("stop", { workflow_id: $scope.workflow.data.id });

        let fids = [];
        for (let i = 0; i < floworder.length; i++) {
            let fid = floworder[i].id;
            fids.push(fid);
        }
        await wiz.API.async("run", { workflow_id: $scope.workflow.data.id, flow_id: fids.join(",") });
    }

    window.appRun = async (flow_id) => {
        await $scope.workflow.save(true);
        await wiz.API.async("run", { workflow_id: $scope.workflow.data.id, flow_id: flow_id });
    }

    window.appStop = $scope.workflow.stop = async (flow_id) => {
        await wiz.API.async("stop", { workflow_id: $scope.workflow.data.id, flow_id: flow_id });
    }

    $scope.workflow.kill = async () => {
        await wiz.API.async("kill", { workflow_id: $scope.workflow.data.id });
    }

    $scope.workflow.restart = async () => {
        await wiz.API.async("restart", { workflow_id: $scope.workflow.data.id });
    }

    window.appDisplay = async (flow_id) => {
        $scope.workflow.display = false;
        await $timeout();
        $('#offcanvas-app-viewer').offcanvas('show');
        await $scope.workflow.save(true);
        $('#offcanvas-app-viewer iframe').attr('src', "/dizest/ui/viewer/" + $scope.workflow.data.id + "/" + flow_id);
        $('#offcanvas-app-viewer iframe').on('load', async () => {
            $scope.workflow.display = true;
            await $timeout();
        });
    }

    let counter = 0;
    window.appCode = $scope.app.code = async (flow_id) => {
        counter++;
        if (flow_id != 'new') {
            await $scope.workflow.save(true);
            let connected = wiz.connect("page.hub.app.editor");
            await connected.data({
                workflow_id: $scope.workflow.data.id,
                flow_id: flow_id,
                layout: counter == 1 ? 4 : null,
                socket: $scope.socket,
                view: "editor",
                save: async () => {
                    let appid = flow_id.split("-")[0];
                    await appLoader(appid, true);
                    await $scope.drawflow_init();
                },
                run: async () => {
                    await window.appRun(flow_id);
                },
                stop: async () => {
                    await window.appStop(flow_id);
                }
            }).event("load");
            await $timeout();
            $('#offcanvas-app-code').offcanvas('show');
        } else {
            $('#offcanvas-app-code').offcanvas('show');
            let connected = wiz.connect("page.hub.app.editor");
            await connected.data({
                workflow_id: 'develop',
                flow_id: "new",
                layout: counter == 1 ? 4 : null,
                view: "editor"
            }).event("load");

            await $scope.apps.load.current();
        }
    }

    window.appInfo = $scope.app.info = async (appid) => {
        let app = await appLoader(appid);
        $scope.app.data = app;
        $scope.app.description.data.set($scope.app.data.description);
        await $timeout();
        $('#offcanvas-app-info').offcanvas('show');
    }

    window.positionMobile = (ev) => {
        mobile_last_move = ev;
    }
    window.allowDrop = (ev) => {
        ev.preventDefault();
    }
    window.drag = function (ev) {
        if (ev.type === "touchstart") {
            mobile_item_selec = ev.target.closest(".drag-drawflow").getAttribute('data-node');
        } else {
            ev.dataTransfer.setData("node", ev.target.getAttribute('data-node'));
        }
    }
    window.drop = (ev) => {
        if (ev.type === "touchend") {
            let parentdrawflow = document.elementFromPoint(mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY).closest("#drawflow");
            if (parentdrawflow != null) {
                addNodeToDrawFlow(mobile_item_selec, mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY, null, null, true);
            }
            mobile_item_selec = '';
        } else {
            ev.preventDefault();
            let data = ev.dataTransfer.getData("node");
            addNodeToDrawFlow(data, ev.clientX, ev.clientY, null, null, true);
        }
    }

    let addNodeToDrawFlow = $scope.addNodeToDrawFlow = async (name, pos_x, pos_y, nodeid, data, isdrop) => {
        if (!data) data = {};
        if (editor.editor_mode === 'fixed') {
            return false;
        }

        let pos = new DOMMatrixReadOnly(editor.precanvas.style.transform);
        if (!pos_x) {
            pos_x = -pos.m41 + 24
        } else if (isdrop) {
            pos_x = pos_x * (editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)) - (editor.precanvas.getBoundingClientRect().x * (editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)));
        }

        if (!pos_y) {
            pos_y = -pos.m42 + 24
        } else if (isdrop) {
            pos_y = pos_y * (editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)) - (editor.precanvas.getBoundingClientRect().y * (editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)));
        }

        let item = await appLoader(name, false);
        if (!item) return;

        if (!nodeid)
            nodeid = item.id + "-" + new Date().getTime();
        let inputs = [];
        for (let i = 0; i < item.inputs.length; i++) {
            let value = item.inputs[i];
            if (value.type == 'output') {
                inputs.push("input-" + value.name);
            }
        }

        let outputs = [];
        for (let i = 0; i < item.outputs.length; i++) {
            let value = item.outputs[i];
            outputs.push("output-" + value.name);
        }

        editor.addNode(nodeid, item.title, inputs, outputs, pos_x, pos_y, "flow-" + nodeid + ' ' + nodeid + ' ' + item.id + ' ' + item.mode, data, create_html(nodeid, item));
    }

    // init
    $scope.drawflow_init = async () => {
        $scope.drawflow_clear = true;
        await $timeout();

        $scope.drawflow_clear = false;
        await $timeout();

        let id = document.getElementById("drawflow");
        editor = $scope.drawflow = new Drawflow(id);
        editor.reroute = true;
        editor.reroute_fix_curvature = true;
        editor.force_first_input = false;
        editor.start();

        if ($scope.workflow.data.flow) {
            let flowdata = $scope.workflow.data.flow;

            for (let key in flowdata) {
                let item = flowdata[key];
                let inputs = [];
                for (let inputkey in item.inputs) inputs.push(inputkey);
                let outputs = [];
                for (let outputkey in item.outputs) outputs.push(outputkey);
                let app_id = item.id.split("-")[0];
                await addNodeToDrawFlow(app_id, item.pos_x, item.pos_y, item.id, item.data);
            }

            for (let key in flowdata) {
                let item = flowdata[key];
                let id_input = item.id;
                for (let input_class in item.inputs) {
                    let conn = item.inputs[input_class].connections;
                    for (let i = 0; i < conn.length; i++) {
                        let id_output = conn[i].node;
                        let output_class = conn[i].input;
                        try {
                            editor.addConnection(id_output, id_input, "output-" + output_class, "input-" + input_class);
                        } catch (e) {
                        }
                    }
                }

                let id_output = item.id;
                for (let output_class in item.outputs) {
                    let conn = item.outputs[output_class].connections;
                    for (let i = 0; i < conn.length; i++) {
                        id_input = conn[i].node;
                        let input_class = conn[i].output;
                        try {
                            editor.addConnection(id_output, id_input, "output-" + output_class, "input-" + input_class);
                        } catch (e) {
                        }
                    }
                }
            }
        }

        for (let flow_id in $scope.workflow.data.flow)
            socket.emit("status", { workflow_id: $scope.workflow.data.id, flow_id: flow_id });
    }

    $scope.fullsize = async (stat) => {
        if (stat) $scope.appcodewidth = '100vw';
        else $scope.appcodewidth = '860px';
        await $timeout();
    }

    await $scope.drawflow_init();
    await $scope.apps.load.installed(true);
    if ($scope.workflow.floworder.length == 0)
        await $scope.apps.load.private(true);

    $scope.workflow.loaded = true;
    await $timeout();
}