if (jQuery) {
    $j(document).ready(function(){
        if ( $j.browser.msie ) {
            $j(":checkbox").click(function(){
                $j(this).change();
            });
        }
        $j(".enableDisable").each(function(){
            var group = $j(this);
            var disableFn = function() {
                group.children("#disabled").fadeTo(250,0.33); 
                group.children("#disabled").find(":checkbox").attr("checked",false);
                group.children("#disabled").find("input[type$='text']").val(""); 
                group.children("#disabled").find("input").attr("disabled",true);
            };
            var enableFn = function () {
                group.children("#disabled").fadeTo(250,1);
                group.children("#disabled").find("input").attr("disabled",false);
            };
            disableFn();
            $j(this).children("#trigger").find(":checkbox:first").change(function() {
                var checked = $j(this).attr("checked");
                if (checked == true) {
                    enableFn();
                } else {
                    disableFn();
                }
            });
        });
        $j(".checkboxGroup").each(function(){
            var group = $j(this);
            var uncheckAll = function(){
                group.find("input[type$='checkbox']").attr("checked",false);
                group.find("input[type$='checkbox']").change();
            };
            var uncheckRadioAndAll = function(){
                group.find("#checkboxAll,#checkboxRadio").find("input[type$='checkbox']").attr("checked",false);
                group.find("#checkboxAll,#checkboxRadio").find("input[type$='checkbox']").change();
            };
            
            group.find("#checkboxAll").find("input").click( 
                function(){
                    var flip;
                    var checked = $j(this).siblings(":checkbox:first").attr("checked");
                    if($j(this).attr("name") == $j(this).parents("#checkboxAll:first").find(":checkbox:first").attr("name")){
                        checked = $j(this).attr("checked");
                        flip = checked;
                    }else{
                        flip = !checked;
                    }
                    if($j(this).attr("type") == "text") if(flip == false) flip = !filp;
                    uncheckAll();
                    $j(this).parents("#checkboxAll:first").find(":checkbox").attr("checked",flip);
                    $j(this).parents("#checkboxAll:first").find(":checkbox").change();
                }
            );
            
            group.find("#checkboxRadio").find("input[type$='checkbox']").click(function(){
                uncheckAll();
                $j(this).siblings("input[type$='checkbox']").attr("checked",false);
                $j(this).attr("checked",true);
                $j(this).change();
            });
            
            group.find("#checkboxCheckbox").click(
                function(){
                    uncheckRadioAndAll();
                }
            );
        });
        
    });
}
