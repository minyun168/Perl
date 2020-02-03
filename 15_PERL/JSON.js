function JSON(){}
JSON.Encode=
   function(obj){
    var rtn;
    if(obj==null){
        rtn = "null";
    }else{
        switch(obj.constructor){
            case Boolean:
                rtn = obj?"true":"false";
                break;
            case Number:
                rtn = isNaN(obj)||!isFinite(obj)?"null":obj.toString(10);
                break;
            case String:
                  rtn = "\""+JSON.Util(obj)+"\"";
                break;
            case Array:
                var buf = [];
                for(var i=0;i<obj.length;i++){
                    //再帰呼出
                    buf.push(arguments.callee(obj[i]));
                }
                rtn = "["+buf.join(",")+"]";
                break;
            case Object:
                var buf = [];
                for(var key in obj){
                    if(obj.hasOwnProperty(key)){
                        buf[buf.length] = arguments.callee(key)+":"+arguments.callee(obj[key]);
                    }
                }
                rtn = "{"+buf.join(",")+"}";
                break;
            default:
                rtn = "null";
                break;
        }
    }
    return rtn;
}

JSON.EncodeComplete=
   function(obj){
    var rtn;
    if(obj==null){
        rtn = "null";
    }else{
        switch(obj.constructor){
            case Boolean:
                rtn = obj?"true":"false";
                break;
            case Number:
                rtn = isNaN(obj)||!isFinite(obj)?"null":obj.toString(10);
                break;
            case String:
                rtn = "\""+JSON.Util(obj)+"\"";
                break;
            case Array:
                var buf = [];
                for(var i=0;i<obj.length;i++){
                    buf.push(arguments.callee(obj[i]));
                }
                rtn = "["+buf.join(",")+"]";
                break;
            case Object:
                var buf = [];
                for(var key in obj){
                    if(obj.hasOwnProperty(key)){
                        buf[buf.length] = arguments.callee(key)+":"+arguments.callee(obj[key]);
                    }
                }
                rtn = "{"+buf.join(",")+"}";
                break;
            default:
                rtn = "null";
                break;
        }
    }
    return rtn;
}

JSON.Decode=
   function(str){
    var rtn;
    eval("rtn="+str);
    return rtn;
}

JSON.Util=
function(str){
    return          str .
                    replace(/\\/ig  ,   "\\\\"      ).
                    replace(/\f/ig  ,   "\\f"       ).
                    replace(/\n/ig  ,   "\\n"       ).
                    replace(/\r/ig  ,   "\\r"       ).
                    replace(/\t/ig  ,   "\\t"       ).
                    replace(/&apos;/ig   ,   "\\&apos;"       ).
                    replace(/"/ig   ,   "\\\""      )       .
                    replace(/</ig  ,   "＜").
                    replace(/>/ig  ,   "＞").
                    replace(/&/ig  ,   "＆").
                    replace(/;/ig  ,   "；");
}
