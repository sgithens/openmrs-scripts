var openmrs = openmrs || {};
openmrs.htmlformentry = openmrs.htmlformentry || {};

/**
 * Updates the specific datetime in an observation widget, depending
 * on whether it's checkbox is ticked or not.
 */
openmrs.htmlformentry.updateObsDateTime = function(id, dateval) {
    $j("#"+id+" input[type='checkbox']").each(function(idx,e) {
        var newval = dateval;
        if ($j(this).is(':checked') === false) {
            newval = "";
        }
        $j("#"+id+" input[onclick='showCalendar(this)']").each(function(idx,e) {
            $j(this).val(newval);
        });
    });
}

/**
 * This function initializes a set of obs tags that are rendered as 
 * checkboxes (usually coded concept answers) to all be bound to a single
 * obs.datetime widget.
 */
openmrs.htmlformentry.initDetachedObsDatetime = function(obsDatetimeId,obsCheckboxIds) {
    alert("90 Gah!");
    for (var i = 0; i < obsCheckboxIds.length; i++) { 
        // Do an initial check for errors in case we're in an encounter.
        $j("#"+obsCheckboxIds[i]+" > span.error").each(function(idx,e) {  //.filter(":last").each(function(idx,e) { 
           var newerr = $j(e).clone(); 
           if ($j(e).html().length > 3) {
                $j("#"+obsDatetimeId).after(newerr);
           }
        });
        // Do an initial run through in case we're loading a previous encounter.
        $j("#"+obsCheckboxIds[i]+" input[type='checkbox']").each(function(idx,e) {
            if ($j(this).is(':checked') !== false) {
                $j("#"+obsCheckboxIds[i]+" input[onclick='showCalendar(this)']").each(function(idx,e) {
                    if ($j(this).val() !== "") {
                        $j("#"+obsDatetimeId).val($j(this).val());
                    }
                });
            }
        });
        // Hide the obs.datetime widgets
        $j("#"+obsCheckboxIds[i]+" input[onclick='showCalendar(this)']").each(function(idx,e) {
            $j(this).hide();
        });
        // Hide the (dd/mm/yyyy)
        $j("#"+obsCheckboxIds[i]).contents().filter(function(idx) { 
            if (this.nodeType === 3 && idx === 4) {
                // alert("Hmm 7: " + this.nodeValue + "  " + idx);
                this.nodeValue = "";
            }
        });
    }
    // Bind the individual checkboxes
    for (var i = 0; i < obsCheckboxIds.length; i++) {
        $j("#"+obsCheckboxIds[i]+" input[type='checkbox']").change(function() {
            var newdate = $j("#"+obsDatetimeId).val();
            for (var i = 0; i < obsCheckboxIds.length; i++) {
                openmrs.htmlformentry.updateObsDateTime(obsCheckboxIds[i], newdate);
            }
        });
    }
    // Bind the obs.datetime widget we're using.
    $j("#"+obsDatetimeId).change(function() {
        var newdate = $j("#"+obsDatetimeId).val();
        for (var i = 0; i < obsCheckboxIds.length; i++) {
            openmrs.htmlformentry.updateObsDateTime(obsCheckboxIds[i], newdate);
        }
    });
};

/* Currently this initialization must be done in a window load listener rather
 * than a document ready listener, or as inline html. This is because the showError
 * calls made by HTML Form Entry happen in a document ready listener, and if they
 * happen after our document ready listener we'd have to monkey patch showError in 
 * order to update our obs widgets in case there is an error being rendered that
 * we need to copy.
 * 
 * In modern versions of jQuery there isn't a great way to control or observer the 
 * order of execution of the document ready array, so we use load instead here.
 */
// $j(window).load(function() {
//     alert("using load6");
//     openmrs.htmlformentry.initDetachedObsDatetime("combinedDate",["pos7381","neg7381"]);
// });
