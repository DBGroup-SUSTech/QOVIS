<template>
  <div class="dag-container">
    <svg ref="svg" @click="clickSvg">
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from 'vuex';
import dagreD3 from "dagre-d3";
import * as d3 from "d3";
import {Plan} from "@/js/plan/Plan"

export default {
  name: 'Dag',
  props: {
    'plan': Plan
  },
  components: {
  },
  data() {
    return {
      svgEl: null,
      planTree: null,
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
    if (this.plan != null) {
      this.computeDag()
    }
  },
  methods: {
    computeDag() {
      let g = new dagreD3.graphlib.Graph();

      g.setGraph({
        rankdir:'BT',
        ranksep: '20',
      });
      Array.from(this.plan.nodeMap.values()).forEach(node => {
        // const color = node.marked ? '#d0e8ff' : '#eaeaea'
        const color = '#eaeaea'
        g.setNode(node.vid, {
          label: node.toString(),
          style: `fill: ${color}; stroke: #000; font-size: 1.5em;`
        })
      })
      Array.from(this.plan.nodeMap.values()).forEach(node => {
        node.providers.forEach(p => {
          g.setEdge(p.vid, node.vid, {
            style: "fill:#fff;stroke:#333;stroke-width:1.5px"
          })
        })
      })

      let render = new dagreD3.render();
      let svgGroup = d3.select(this.svgEl).append('g');
      render(svgGroup, g)

      const that = this
      function createTooltip() {
        return d3.select(that.$el)
            .append('div')
            .classed('tooltip', true)
            .style('opacity', 0)
            .style('display', 'none');
      }
      let tooltip = createTooltip();
      function tipVisible(textContent) {
        tooltip
            .style('opacity', 0.9)
            .style('display', 'block');
        tooltip.html(textContent)
      }
      // function tipHidden() {
      //   tooltip
      //       .style('opacity', 0)
      //       .style('display', 'none');
      // }

      svgGroup.selectAll("g.node")
          .on("click", function (/*event*/) {
            const node = that.plan.nodeMap.get(parseInt(this.__data__))
            console.log(that.plan, this.__data__, node)
            tipVisible(node.str)
          })


      // let xRange = d3.extent(this.planDag.nodes, node => node.x);
      // let yRange = d3.extent(this.planDag.nodes, node => node.y);
      // let maxWidth = d3.max(this.planDag.nodes, node => node.width)
      // let maxHeight = d3.max(this.planDag.nodes, node => node.height)
      // let _x1 = xRange[0],
      //     _x2 = xRange[1] + maxWidth,
      //     _y1 = yRange[0],
      //     _y2 = yRange[1] + maxHeight;

      const {width, height} = d3.select(this.svgEl)
          .select(".nodes")
          .node().getBBox();
      d3.select(this.svgEl)
          .attr('width', width)
          .attr('height', height)
    },
    computeTextWidth(text) {
      const dom = document.createElement('span')
      dom.style.display = 'inline-block'
      dom.textContent = text
      document.body.appendChild(dom)
      const width = dom.clientWidth
      document.body.removeChild(dom)
      return width
    },
    clickSvg() {
      console.log(this.plan)
    }
  },
  computed: {
    ...mapState('test', {}),
  }
}
</script>

<style scoped>
.dag-container {
  padding: 10px;
}
.dag-container >>> .tooltip {
  text-align: left;
  /*white-space: nowrap;*/
}
</style>
