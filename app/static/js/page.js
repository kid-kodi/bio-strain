$(function() {
    $("div[data-toggle=fieldset]").each(function() {
        var $this = $(this);

        //Add new entry
        $this.find("button[data-toggle=fieldset-add-row]").click(function() {
            var target = $($(this).data("target"));
            console.log(target);
            var oldrow = target.find("[data-toggle=fieldset-entry]:last");
            var row = oldrow.clone();
            console.log(row);
            row.find('.custom-combobox').remove();
            var elem_id = row.find(":input")[0].id;
            var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-.*/m, '$1')) + 1;
            row.attr('data-id', elem_num);
            row.find(":input,select").each(function() {
                console.log(this);
                //$( ".itemBox" ).combobox({ select: onItemChange });
                if($(this).attr('id')!=undefined){
                    var id = $(this).attr('id').replace('-' + (elem_num - 1) + '-', '-' + (elem_num) + '-');
                    $(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
                }
            });
            row.show();
            oldrow.after(row);
            $( ".itemBox" ).combobox({ select: onItemChange });
            //bind();
        }); //End add new entry
    });

    var onCustomerChange = function( event, ui ) {
        var customer_id = ui.item.value;
        $.get('/api/v1.0/customers/'+customer_id, function(data, status){
            console.log( data );
            $('input.customer_email').val(data.email);
            $('textarea.billing_address').val(data.address);
        });
    };

    var onItemChange = function( event, ui ) {
        var item_id = ui.item.value;
        var row = $(this).closest("[data-toggle=fieldset-entry]");
        $.get('/api/v1.0/items/'+item_id, function(data, status){
            console.log( data );
            row.find("input.item_id").val(data.id);
            row.find("input.item_price").val(data.sale_price);
            row.find("input.item_quantity").val(1);
            row.find("input.item_cost").val(data.sale_price);
            row.find(".cost").html(data.sale_price);

            update_total();
        });
    };


    function print_today() {
      // ***********************************************
      // AUTHOR: WWW.CGISCRIPT.NET, LLC
      // URL: http://www.cgiscript.net
      // Use the script, just leave this message intact.
      // Download your FREE CGI/Perl Scripts today!
      // ( http://www.cgiscript.net/scripts.htm )
      // ***********************************************
      var now = new Date();
      var months = new Array('January','February','March','April','May','June','July','August','September','October','November','December');
      var date = ((now.getDate()<10) ? "0" : "")+ now.getDate();
      function fourdigits(number) {
        return (number < 1000) ? number + 1900 : number;
      }
      var today =  months[now.getMonth()] + " " + date + ", " + (fourdigits(now.getYear()));
      return today;
    }

    // from http://www.mediacollege.com/internet/javascript/number/round.html
    function roundNumber(number,decimals) {
      var newString;// The new rounded number
      decimals = Number(decimals);
      if (decimals < 1) {
        newString = (Math.round(number)).toString();
      } else {
        var numString = number.toString();
        if (numString.lastIndexOf(".") == -1) {// If there is no decimal point
          numString += ".";// give it one at the end
        }
        var cutoff = numString.lastIndexOf(".") + decimals;// The point at which to truncate the number
        var d1 = Number(numString.substring(cutoff,cutoff+1));// The value of the last decimal place that we'll end up with
        var d2 = Number(numString.substring(cutoff+1,cutoff+2));// The next decimal, after the last one we want
        if (d2 >= 5) {// Do we need to round up at all? If not, the string will just be truncated
          if (d1 == 9 && cutoff > 0) {// If the last digit is 9, find a new cutoff point
            while (cutoff > 0 && (d1 == 9 || isNaN(d1))) {
              if (d1 != ".") {
                cutoff -= 1;
                d1 = Number(numString.substring(cutoff,cutoff+1));
              } else {
                cutoff -= 1;
              }
            }
          }
          d1 += 1;
        }
        if (d1 == 10) {
          numString = numString.substring(0, numString.lastIndexOf("."));
          var roundedNum = Number(numString) + 1;
          newString = roundedNum.toString() + '.';
        } else {
          newString = numString.substring(0,cutoff) + d1.toString();
        }
      }
      if (newString.lastIndexOf(".") == -1) {// Do this again, to the new string
        newString += ".";
      }
      var decs = (newString.substring(newString.lastIndexOf(".")+1)).length;
      for(var i=0;i<decimals-decs;i++) newString += "0";
      //var newNumber = Number(newString);// make it a number if you like
      return newString; // Output the result to the form field (change for your purposes)
    }

    function update_total() {
      var total = 0;
      $('.item_cost').each(function(i){
        cost = $(this).val();
        if (!isNaN(cost)) total += Number(cost);
      });

      total = roundNumber(total,2);

      $('.amount_due').val(total);
      $('.amount_paid').val(0);

      $('.amount_due_text').html(total+'F.CFA');
      $('.amount_paid_text').html("0");
    }

    function update_price() {
      var row = $(this).parents('.item-row');
      var item_cost = row.find('.item_price').val() * row.find('.item_quantity').val();
      item_cost = roundNumber(item_cost,2);
      isNaN(item_cost) ? row.find('.cost').html("N/A") : row.find('.cost').html(item_cost);
      row.find('.item_cost').val(item_cost);
      row.find('.cost').html(item_cost);

      update_total();
    }

    var onDeleteBtnClick = function(){
        alert( $('.table tbody tr').length );
        if ($('.table tbody tr').length > 1){
            $(this).parents('tr').first().remove();
            update_total();
        }
    }

    var onDataPrint = function (argument) {
      var items = [];
      $('input[name=items]:checked').map(function() {
          items.push($(this).val());
      });


      $.ajax({
          url: "/trainee/print",
          type: "POST",
          data: JSON.stringify({"items":items}),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            console.log(data);
            var trainees = data.trainees;
            $('#printableArea').html('')
            for (i = 0; i < trainees.length; i++) {
                $('#printableArea').append( addTemplateToList(trainees[ i ]) );
            }
            printDiv();
          }
      });

      return false;
    };

    var addTemplateToList = function( data ){
        html = String()
        + '<div class="col-md-3">'
            + '<div class="trainee-card">'
                + '<div class="trainee-card-head">'
                    + '<div class="trainee-card-head-logo">'
                        + '<img src="img/logo.png" style="width: 40px; height: 30px">'
                        + '<p style="height: 10px">STAGIAIRE</p>'
                        + '<b class="reg_number">' + data.registration_number + '</b>'
                    + '</div>'
                    + '<div class="trainee-card-head-avtr">'
                        + '<img src="' + data.image_url + '" style="width: 40px; height: 40px">'
                    + '</div>'
                + '</div>'
                + '<div class="trainee-card-body">'
                    + '<h3 class="full_name">' + data.first_name + ' ' + data.last_name + '</h3>'
                    + '<ul>'
                    +    '<li>Departement : <b>' + data.unit.department + '</b></li>'
                    +    '<li>Unité : <b>' + data.unit + '</b></li>'
                    +    '<li>Niveau d\'étude : <b>' + data.level + '</b></li>'
                    +    '<li>Etabl. d\'origine : <b>' + data.school + '</b></li>'
                    +    '<li>Tuteur : <b>' + data.responsable + '</b></li>'
                    + '</ul>'
                + '</div>'
                + '<div class="trainee-card-footer">'
                +    '<em>Valable jusqu\'au ' + data.ended_date + '</em>'
                + '</div>'
        +   '</div>'
        + '</div>'

        return html;
    }

    var printDiv = function() {
         var divName = 'printableArea';
         var printContents = document.getElementById(divName).innerHTML;
         var originalContents = document.body.innerHTML;

         document.body.innerHTML = printContents;

         window.print();

         document.body.innerHTML = originalContents;
    };

    $('.chkAllBtn').click(function() {
        var isChecked = $(this).prop("checked");
        $('table tr:has(td)').find('input[type="checkbox"]').prop('checked', isChecked);
    });

    $('table tr:has(td)').find('input[type="checkbox"]').click(function() {
        var isChecked = $(this).prop("checked");
        var isHeaderChecked = $(".chkAllBtn").prop("checked");
        if (isChecked == false && isHeaderChecked)
            $(".chkAllBtn").prop('checked', isChecked);
        else {
            $('table tr:has(td)').find('input[type="checkbox"]').each(function() {
                if ($(this).prop("checked") == false)
                    isChecked = false;
            });
            $(".chkAllBtn").prop('checked', isChecked);
        }
    });


    $( ".customerBox" ).combobox({ select: onCustomerChange });

    $( ".itemBox" ).combobox({ select: onItemChange });

    $('body').on('click', '.printBtn', onDataPrint);
    //$('body').on('click', '.printDiv', printDiv);

    $( ".datepicker" ).datepicker();

    $('#order').on('keyup', '.item_price',    update_price     );
    $('#order').on('keyup', '.item_quantity', update_price     );
    $('#order').on('click', '.remove_row',    onDeleteBtnClick );

});
