/* global loaSettings */

$(document).ready(function () {
    "use strict";

    var listPendingRequestsUrl = loaSettings.listPendingRequestsUrl;

    var csrfToken = loaSettings.csrfToken;
    function viewRequestModalUrl(id) {
        return loaSettings.viewRequestModalUrl.replace("12345",id);
    }
    function approveRequestUrl(id) {
        return loaSettings.approveRequestUrl.replace("12345",id);
    }
    function cancelRequestUrl(id) {
        return loaSettings.cancelRequestUrl.replace("12345",id);
    }
    var csrfToken = loaSettings.csrfToken;

    /* dataTable def */
    $("#table-requests").DataTable({
        ajax: {
            url: listPendingRequestsUrl,
            dataSrc: "",
            cache: false,
        },

        columns: [
            { data: "user" },
            { data: "start" },
            { data: "end" },
            { data: "pk", className: "right-column" },
        ],

        lengthMenu: [
            [10, 25, 50, 100, -1],
            [10, 25, 50, 100, "All"],
        ],


        columnDefs: [
            { sortable: false, targets: [3] },
            {
                render: function (data, type, row) {
                    if (type === "display") {
                        return (
                            '<div style="white-space: nowrap;"><button class="btn btn-info btn-sm btn-square" data-toggle="modal" data-target="#modalViewRequestContainer" data-ajax_url="' +
                                viewRequestModalUrl(data) +
                                '" aria-label="Request Info"><span class="fas fa-info-circle"></span></button>&nbsp;' +
                            '<form method="post" class="inline" action="' + cancelRequestUrl(data) + '">' +
                        csrfToken +
                            '<button type="submit" class="btn btn-sm btn-danger btn-square">' +
                            '<span class="fas fa-trash-alt"></span>' +
                            '</button></form>&nbsp;' +
                            '<form method="post" class="inline" action="' + approveRequestUrl(data) + '">' +
                        csrfToken +
                            '<button type="submit" class="btn btn-sm btn-primary btn-square">' +
                            '<span class="fas fa-check"></span>' +
                            '</button></form></div>'
                        );
                    }

                    return data;
                },
                targets: [3],
            },
        ],

        order: [
            [0, "desc"],
        ],
    });
});
