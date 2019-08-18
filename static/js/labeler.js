let img_name;
let found_labels = [];

$(document).ready(function () {
    let url = window.location.href;
    img_name = url.split('/')[url.split('/').length - 1];
    $.get("/label_img/" + img_name).done(function (data) {
            if (data !== "Failed") {
                let labels_path = JSON.parse(data);
                let all_labels_objects = {
                    "Receipt": [$("#receipt"), "get_receipt", "receipt"],
                    "Logo": [$("#logo"), "get_logo", "logo"],
                    "Shop details": [$("#sd"), "get_sd", "sd"],
                    "Purchase summary": [$("#ps"), "get_ps", "ps"],
                    "Additional details": [$("#ad"), "get_ad", "ad"]
                };
                show(all_labels_objects, labels_path, url)
            } else {
                return_to_index()
            }
        }
    );

});

window.addEventListener('beforeunload', function () {
    return_to_index();
});

function return_to_index() {
    window.location.replace((window.location.href).replace("labeler/" + img_name, ''));

}

function chagne_element_attributes(img, attributes) {
    let url = window.location.href;
    let src_path = url.replace("/labeler/", "/" + img["get_label"] + "/");
    img["original_width"] = attributes["width"];
    img["original_height"] = attributes["height"];
    img["object"].attr({
        'src': src_path
    });
}

function show_dialog(text, title, create, close) {
    $(".dialog").dialog({
        create: function () {
            this.innerHTML = text;
            create();
        },
        close: function () {
            close();
        },
        title: title,
        modal: true,
        dialogClass: 'dialog',
        width: "484px",
        hide: null,
        buttons: [
            {
                text: "Ok",
                click: function () {
                    $(this).dialog("close");
                },
            }
        ]
    }).prev(".ui-dialog-titlebar").css({"background": "#165D79", "color": "rgb(222, 240, 247)"});
}

function show(all_labels_objects, labels_path, url) {
    let not_found_labels = Object.keys(all_labels_objects).reduce((acc, curr) => {
        if (!Object.keys(labels_path).includes(curr)) {
            acc.push({"label_name": curr, "object": all_labels_objects[curr][0], "id": all_labels_objects[curr][2]})
        }
        return acc
    }, []);

    let not_found_labels_str = "";
    for (let i in not_found_labels) {
        if (not_found_labels[i]["label_name"] === "Receipt") {
            let text = "Not a valid receipt image!<br>Press OK to rescan";
            show_dialog(text, "Receipt not valid!",
                function () {
                    $(".loader").hide();
                    $(".blank").show();
                },
                function () {
                    return_to_index()
                });
            return
        }
        not_found_labels[i]["object"].parent().remove();
        $("." + not_found_labels[i]["id"] + "_labels_container").remove();
        not_found_labels_str += not_found_labels[i]["label_name"] + ", ";
    }

    found_labels = Object.keys(all_labels_objects).reduce((acc, curr) => {
        if (Object.keys(labels_path).includes(curr)) {
            let curr_params = all_labels_objects[curr];
            acc.push({
                "label_name": curr,
                "object": curr_params[0],
                "get_label": curr_params[1],
                "original_width": 0,
                "original_height": 0
            })
        }
        return acc
    }, []);
    for (let i in found_labels) {
        if (found_labels.hasOwnProperty(i)) {
            let label_name = found_labels[i]["label_name"];
            let params = labels_path[label_name];
            chagne_element_attributes(found_labels[i], params);
        }
    }
    $(".label_name")[0].innerText = "Receipt";
    $(".preview_img").attr({'src': url.replace("/labeler/", "/get_receipt/")});

    if (not_found_labels.length !== 0) {
        let text = "Labels:<br><text style='font-weight:900;'>" + not_found_labels_str.substring(0, not_found_labels_str.length - 2) + "</text><br>wasn't found!<br>Rescan the receipt or scan a new one!"
        ;
        show_dialog(text, "Some labels not found...",
            function () {
                $(".loader").hide();
                $(".images_and_preview").show();
                $(".load_and_alert").css("height", "auto");
                $(".blank").hide();
            },
            function () {
                $(".load_and_alert").hide();
            }
        );
    } else {
        $(".loader").hide();
        $(".images_and_preview").show();
        $(".load_and_alert").hide();
    }
}


function view_image(img) {
    let width_height = found_labels.reduce((acc, curr) => {
        if (curr["label_name"] === img.title) acc = [curr["original_width"], curr["original_height"]];
        return acc;
    }, []);
    let width = width_height[0];
    let height = width_height[1];
    let preview_img = $(".preview_img");
    if (width > 280)
        width = "280px";
    if (height > 450)
        height = "500px";
    preview_img.attr("src", img.src);
    preview_img.css({"width": width, "height": height});
    $(".label_name")[0].innerText = img.title;
    $(".preview").css({"display": "inline-block"});
}

