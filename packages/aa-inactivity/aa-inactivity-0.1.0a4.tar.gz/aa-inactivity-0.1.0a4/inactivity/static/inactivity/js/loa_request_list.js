/* global loaSettings */

$(document).ready(function () {
    "use strict";

    var listRequestsUrl = loaSettings.listRequestsUrl;
    var csrfToken = loaSettings.csrfToken;
    function cancelRequestUrl(id) {
        return loaSettings.cancelRequestUrl.replace("12345",id);
    }
    var csrfToken = loaSettings.csrfToken;

    /* dataTable def */
    $("#table-requests").DataTable({
        ajax: {
            url: listRequestsUrl,
            dataSrc: "",
            cache: false,
        },

        columns: [
            { data: "start" },
            { data: "end" },
            { data: "approved" },
            { data: "pk" },
        ],

        lengthMenu: [
            [10, 25, 50, 100, -1],
            [10, 25, 50, 100, "All"],
        ],


        columnDefs: [
            { sortable: false, targets: [2, 3] },
            {
                render: function (data, type, row) {
                    if (type === "display") {
                        if (data) {
                            return '<span class="fas fa-check-circle text-success" aria-label="Yes"></span>';
                        } else {
                            return '<span class="fas fa-times-circle text-danger" aria-label="No"></span>';
                        }
                    }

                    return data;
                },
                targets: [2],
            },
            {
                render: function (data, type, row) {
                    if (type === "display") {
                        return (
                            '<form method="post" class="inline" action="' + cancelRequestUrl(data) + '">' +
                        csrfToken +
                            '<button type="submit" class="btn btn-sm btn-danger btn-square">' +
                            '<span class="fas fa-trash-alt"></span>' +
                            '</button></form>'
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
