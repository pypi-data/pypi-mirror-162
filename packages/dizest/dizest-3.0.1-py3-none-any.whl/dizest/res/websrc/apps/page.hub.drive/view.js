let wiz_controller = async ($sce, $scope, $timeout) => {
    let _$timeout = $timeout;
    $timeout = (timestamp) => new Promise((resolve) => _$timeout(resolve, timestamp));

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

    $scope.download = (file) => {
        return wiz.API.url("download?path=" + $scope.query.path + "/" + encodeURIComponent(file.name));
    }

    let api = async (action, query) => {
        if (!query) query = {};
        query = angular.copy(query);
        query['mode'] = wiz.data.mode;
        let res = await wiz.API.async(action, query);
        if (res.code == 200) {
            return res.data;
        }
        throw Exception(res.data);
    }

    $scope.data = {};
    $scope.data.newitem = {};
    $scope.data.checked = [];
    $scope.loader = false;

    $scope.timer = (value) => {
        return moment(new Date(value * 1000)).format("YYYY-MM-DD HH:mm:ss");
    }

    $scope.filesize = (value) => {
        if (!value) return "--";
        let kb = value / 1024;
        if (kb < 1) return value + "B";
        let mb = kb / 1024;
        if (mb < 1) return Math.round(kb * 100) / 100 + "KB";
        let gb = mb / 1024;
        if (gb < 1) return Math.round(mb * 100) / 100 + "MB";
        return Math.round(gb * 100) / 100 + "GB";
    }

    $scope.mode = wiz.data.mode;
    $scope.query = { path: location.href.split("#")[1] ? decodeURIComponent(location.href.split("#")[1]) : '' };

    $scope.load = async (item) => {
        if (item) {
            if (item.type == 'folder') {
                $scope.query.path = $scope.query.path + "/" + item.name;
                location.href = "#" + $scope.query.path;
            } else {
                return;
            }
        }

        $scope.paths = $scope.query.path.split("/").splice(1);

        $scope.files = await api("ls", $scope.query);
        $scope.files.sort((a, b) => {
            return a.name.localeCompare(b.name);
        });
        $scope.files.sort((a, b) => {
            return b.type.localeCompare(a.type);
        });

        $scope.data.checked = [];
        $scope.data.checked_all = false;
        await $timeout();
    }

    $scope.load_parent = async () => {
        let path = $scope.query.path.split("/");
        path = path.splice(0, path.length - 1);
        path = path.join("/");
        $scope.query.path = path;
        location.href = "#" + $scope.query.path;
        await $scope.load();
    }

    $scope.event = {};
    $scope.event.rename = async (file) => {
        file.rename = file.name;
        file.edit = true;
        await $timeout();
    }

    $scope.event.create = async () => {
        $scope.data.newitem = {};
        await $timeout();
        $('#offcanvas-create-folder').offcanvas("show");
    }

    $scope.event.drop = {};
    $scope.event.drop.text = "Drop File Here!"
    $scope.event.drop.ondrop = async (e, files) => {
        let fd = new FormData();
        let filepath = [];
        fd.append("mode", $scope.mode);
        fd.append("path", $scope.query.path);
        for (let i = 0; i < files.length; i++) {
            fd.append('file[]', files[i]);
            filepath.push(files[i].filepath);
        }
        fd.append("filepath", JSON.stringify(filepath));
        await $scope.api.upload(fd);
    }

    $scope.event.upload = function () {
        $('#file-upload').click();
    };

    let fileinput = document.getElementById('file-upload');
    fileinput.onchange = async () => {
        let fd = new FormData($('#file-form')[0]);
        fd.append("mode", $scope.mode);
        fd.append("path", $scope.query.path);
        await $scope.api.upload(fd);
    };

    $scope.event.check = async (file) => {
        if (!file) {
            let checkstatus = true;
            if ($scope.data.checked.length > 0) {
                checkstatus = false;
                $scope.data.checked = [];
            }

            for (let i = 0; i < $scope.files.length; i++) {
                $scope.files[i].checked = checkstatus;
                if (checkstatus)
                    $scope.data.checked.push($scope.files[i].name);
            }

            $scope.data.checked_all = checkstatus;
            await $timeout();
            return;
        }

        file.checked = !file.checked;
        if (file.checked && !$scope.data.checked.includes(file.name)) {
            $scope.data.checked.push(file.name);
        }
        if (!file.checked) {
            $scope.data.checked.remove(file.name);
        }

        $scope.data.checked_all = $scope.data.checked.length > 0;
        await $timeout();
    }

    $scope.event.loader = async (status) => {
        $scope.loader = status;
        await $timeout();
    }

    $scope.api = {};

    $scope.api.upload = async (data) => {
        let fn = (fd) => new Promise((resolve) => {
            let url = wiz.API.url('upload');
            $.ajax({
                url: url,
                type: 'POST',
                data: fd,
                cache: false,
                contentType: false,
                processData: false
            }).always(function (res) {
                resolve(res);
            });
        });

        await $scope.event.loader(true);
        await fn(data);
        await $scope.load();
        await $scope.event.loader(false);
    };

    $scope.api.rename = async (file) => {
        let data = angular.copy(file);
        data.path = $scope.query.path;
        await api('rename', data);
        await $scope.load();
    }

    $scope.api.remove = async (file) => {
        $scope.event.loader(true);
        let data = angular.copy(file);
        data.path = $scope.query.path;
        await api('delete', data);
        await $scope.load();
        $scope.event.loader(false);
    }

    $scope.api.remove_all = async (files) => {
        $scope.event.loader(true);
        for (let i = 0; i < files.length; i++) {
            let data = { name: files[i], path: $scope.query.path };
            await api('delete', data);
        }
        await $scope.load();
        $scope.event.loader(false);
    }

    $scope.api.create = async (file) => {
        let data = angular.copy(file);
        data.path = $scope.query.path;
        await api('create', data);
        await $scope.load();
        $('#offcanvas-create-folder').offcanvas("hide");
    }

    await $scope.load();
}