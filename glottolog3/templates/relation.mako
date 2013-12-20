<%inherit file="glottolog_comp.mako"/>

<%block name="head">
<script language="javascript" type="text/javascript" src="${request.static_url('clld:web/static/js/jit.js')}"></script>
<style>
#infovis {
    position:relative;
    width:500px;
    height:500px;
    margin:none;
    overflow:visible;
}
</style>
</%block>


<div id="container">

<div id="left-container">



<div class="text">
<h4>
SpaceTree with on-demand nodes
</h4>

            This example shows how you can use the <b>request</b> controller method to create a SpaceTree with <b>on demand</b> nodes<br /><br />
            The basic JSON Tree structure is cloned and appended on demand on each node to create an <b>infinite large SpaceTree</b><br /><br />
            You can select the <b>tree orientation</b> by changing the select box in the right column.

</div>

<div id="id-list"></div>


<div style="text-align:center;"><a href="example2.code.html">See the Example Code</a></div>
</div>

<div id="center-container">
    <div id="infovis"></div>
</div>

<div id="right-container">

<h4>Change Tree Orientation</h4>
<table>
    <tr>
        <td>
            <label for="r-left">left </label>
        </td>
        <td>
            <input type="radio" id="r-left" name="orientation" checked="checked" value="left" />
        </td>
    </tr>
    <tr>
         <td>
            <label for="r-top">top </label>
         </td>
         <td>
            <input type="radio" id="r-top" name="orientation" value="top" />
         </td>
    <tr>
         <td>
            <label for="r-bottom">bottom </label>
          </td>
          <td>
            <input type="radio" id="r-bottom" name="orientation" value="bottom" />
          </td>
    </tr>
    <tr>
          <td>
            <label for="r-right">right </label>
          </td>
          <td>
           <input type="radio" id="r-right" name="orientation" value="right" />
          </td>
    </tr>
</table>
<script>
var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();



function init(data, center){
    //Implement a node rendering function called 'nodeline' that plots a straight line
    //when contracting or expanding a subtree.
    $jit.ST.Plot.NodeTypes.implement({
        'nodeline': {
          'render': function(node, canvas, animating) {
                if(animating === 'expand' || animating === 'contract') {
                  var pos = node.pos.getc(true), nconfig = this.node, data = node.data;
                  var width  = nconfig.width, height = nconfig.height;
                  var algnPos = this.getAlignedPos(pos, width, height);
                  var ctx = canvas.getCtx(), ort = this.config.orientation;
                  ctx.beginPath();
                  if(ort == 'left' || ort == 'right') {
                      ctx.moveTo(algnPos.x, algnPos.y + height / 2);
                      ctx.lineTo(algnPos.x + width, algnPos.y + height / 2);
                  } else {
                      ctx.moveTo(algnPos.x + width / 2, algnPos.y);
                      ctx.lineTo(algnPos.x + width / 2, algnPos.y + height);
                  }
                  ctx.stroke();
              }
          }
        }

    });

    //init Spacetree
    //Create a new ST instance
    var st = new $jit.ST({
        'orientation': 'top',
        'align': 'center',
        //'multitree': true,
        'injectInto': 'infovis',
        //set duration for the animation
        duration: 800,
        //set animation transition type
        transition: $jit.Trans.Quart.easeInOut,
        //set distance between node and its children
        levelDistance: 40,
        //set max levels to show. Useful when used with
        //the request method for requesting trees of specific depth
        levelsToShow: 20,
        //set node and edge styles
        //set overridable=true for styling individual
        //nodes or edges
        Node: {
            height: 30,
            width: 200,
            //use a custom
            //node rendering function
            type: 'nodeline',
            color:'#23A4FF',
            lineWidth: 2,
            align:"center",
            overridable: true
        },

        Edge: {
            type: 'bezier',
            lineWidth: 2,
            color:'#23A4FF',
            overridable: true
        },

        //Add a request method for requesting on-demand json trees.
        //This method gets called when a node
        //is clicked and its subtree has a smaller depth
        //than the one specified by the levelsToShow parameter.
        //In that case a subtree is requested and is added to the dataset.
        //This method is asynchronous, so you can make an Ajax request for that
        //subtree and then handle it to the onComplete callback.
        //Here we just use a client-side tree generator (the getTree function).
        request: function(nodeId, level, onComplete) {
            $.get( "/resource/languoid/id/" + nodeId + ".jit.json", function(data) {
                onComplete.onComplete(nodeId, data);
            });
        },

        onBeforeCompute: function(node){
        },

        onAfterCompute: function(){
        },

        //This method is called on DOM label creation.
        //Use this method to add event handlers and styles to
        //your node.
        onCreateLabel: function(label, node){
            var style = label.style;
            label.id = node.id;
            if (node.data.level == 'dialect') {
                label.innerHTML = '<i>' + node.name + '</i>';
            } else if (node.data.level == 'language') {
                label.innerHTML = '<b>' + node.name + '</b>';
            } else {
                label.innerHTML = node.name;// + '<a href="#' + node.id + '" target="_blank">link</a>';
                label.onclick = function(){
                    st.onClick(node.id);
                };
                style.textDecoration = 'underline';
                style.cursor = 'pointer';
            }
            //set label styles
            //style.overflow = 'hidden';
            style.width = 200 + 'px';
            style.height = 15 + 'px';
            style.color = '#000';
            //style.backgroundColor = '#1a1a1a';
            style.fontSize = '1em';
            style.textAlign= 'center';
            style.paddingTop = '3px';
        },

        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            if (node.selected) {
                node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
            }
        },

        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "#eed";
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    //load json data
    st.loadJSON(data);
    //compute node positions and layout
    st.compute();
    //emulate a click on the root node.
    st.onClick(center == undefined ? st.root : center);
    //end
}

    $(document).ready(function() {
        ${h.JS('init')(data, center)|n};
    });
</script>
