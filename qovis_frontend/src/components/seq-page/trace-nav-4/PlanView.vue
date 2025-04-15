<template>
  <g class="trace-plan-view">
    <defs>
      <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>
      </linearGradient>
      <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('U')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
      </linearGradient>
      <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('A')"/>
        <stop offset="50%" :stop-color="getEvoTypeColor('R')"/>
        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>
      </linearGradient>
      <!--      <linearGradient id="gradient-add" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--      </linearGradient>-->
      <!--      <linearGradient id="gradient-remove" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--      </linearGradient>-->
      <!--      <linearGradient id="gradient-add-remove" x1="0" x2="1" y1="0" y2="1">-->
      <!--        <stop offset="0%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('A')"/>-->
      <!--        <stop offset="25%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('U')"/>-->
      <!--        <stop offset="75%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--        <stop offset="100%" :stop-color="getEvoTypeColor('R')"/>-->
      <!--      </linearGradient>-->
    </defs>
    <g v-for="(block, i) in visTraceTree.planBlocks" :key="i"
         class="plan-item"
         :transform="`translate(${[block.visPlan.x, block.visPlan.y]})`">
<!--      <rect fill="#fafafa" rx="3" ry="3"-->
<!--            stroke="black" stroke-width="2"-->
<!--            :width="block.visPlan.width" :height="block.visPlan.height"></rect>-->
      <g class="plan-group"
         @click="clickPlan(block.visPlan, i)"
         :transform="'translate(' + [planPadding, planPadding] + ')'">
        <g class="edge-group">
          <g v-for="(edge, i) in block.visPlan.edges" :key="i">
            <path :d="edge.path" stroke-width="15"
                  :stroke="'rgb(176,176,176)'"
                  opacity="0.5"
                  fill="none"
                  @click="clickEdge(edge)"
                  :stroke-dasharray="edge.link === '' ? '' : '5 2.5'">
              <title>{{ edge.planEdgeStr }}</title>
            </path>
            <text v-if="edge.planEdgeStr !== ''"
                  class="edge-label"
                  :font-size="edgeFontSize"
                  :dx="edge.textX" :dy="edge.textY + edgeFontSize / 4"
                  text-anchor="middle">
              <tspan>{{ edge.planEdgeStr }}</tspan>
            </text>
          </g>
        </g>
        <g class="node-group">
          <g v-for="(node, i) in block.visPlan.nodes" :key="i" @click="clickNode(node)"
             :transform="'translate(' + [node.x, node.y] + ')'">
            <rect :fill="getEvoFill('U')" rx="3" ry="3"
                  stroke="#7F7F7F"
                  :width="node.width" :height="node.height">
              <title>{{ node.planNodeStr }}</title>
            </rect>

<!--            string node-->
<!--            <text class="node-label"-->
<!--                  :font-size="fontSize"-->
<!--                  :dx="node.width / 2" :dy="nodeTitleHeight - fontSize / 3"-->
<!--                  text-anchor="middle">-->
<!--              <tspan>{{ getNodeName(node) }}</tspan>-->
<!--              <title>{{ node.planNodeStr }}</title>-->
<!--            </text>-->
<!--            <g class="params">-->
<!--              <text v-for="(param, i) in getLimitedParamStrings(node)" :key="i"-->
<!--                    :font-size="fontSize"-->
<!--                    :dx="node.width / 2" :dy="nodeTitleHeight + paramRowHeight * (i + 1) - fontSize / 3"-->
<!--                    text-anchor="middle">-->
<!--                <tspan>{{ getLimitedString(param, node.width, fontSize) }}</tspan>-->
<!--              </text>-->
<!--            </g>-->

            <text class="node-label"
                  :font-size="fontSize"
                  :dx="node.width / 2" :dy="nodeTitleHeight - fontSize / 2"
                  text-anchor="middle">
              <tspan>{{ getNodeName(node) }}</tspan>
              <title>{{ node.planNodeStr }}</title>
            </text>
            <g class="params" :transform="`translate(${[0, nodeTitleHeight]})`">
              <g v-for="(param, i) in node.paramData" :key="i" >
                <g v-for="(row, j) in param[1]" :key="j">
                  <g v-for="(item, k) in row" :key="k">
                    <g class="param-item-rect-group" :id="'p' + item.id"
                       @mouseenter="enterParamRect(block.visPlan, item)"
                       @mouseleave="leaveParamRect(block.visPlan, item)"
                       @click="clickParamRect(item)">
                      <rect :x="item.x" :y="item.y" :width="item.width" :height="item.height"
                            :fill="item.color" rx="5" ry="5"
                            :stroke="getItemColor(item)"
                            :stroke-width="item.isHighlight ? 4 : item.isFixHighlight ? 2.5 : 1">
                        <title>{{ item.content }}</title>
                      </rect>
                      <text :font-size="paramFontSize"
                            :dx="item.x + item.width / 2" :dy="item.y + item.height - paramFontSize / 3"
                            text-anchor="middle">
                        <tspan>{{ item.text }}</tspan>
                        <title>{{ item.content }}</title>
                      </text>
                    </g>
                  </g>

                  <g v-for="(item, k) in row" :key="'mark' + k"
                     class="item-mark">
                    <g v-if="item.isFixHighlight && item.isEqPrev"
                       class="param-item-link-left"
                       :transform="`translate(${[item.x - navIconSize / 2, item.y + item.height / 2 - navIconSize / 2]})`">
                      <svg t="1710230334748" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="11603" xmlns:xlink="http://www.w3.org/1999/xlink" :width="navIconSize" :height="navIconSize">
                        <g @click="clickParamRectLeft(item)">
                          <circle cx="512" cy="512" r="400" fill="white" p-id="11604"></circle>
                          <path :fill="getItemColor(item)"
                                transform="rotate(180 512 512)"
                                d="M512 43.52c-258.56 0-468.48 209.92-468.48 468.48s209.92 468.48 468.48 468.48 468.48-209.92 468.48-468.48-209.92-468.48-468.48-468.48zM398.336 783.36c-23.04-24.576-23.04-62.976 0-88.064l123.904-134.144c23.04-24.576 23.04-62.976 0-87.552L397.824 338.944c-23.04-24.576-23.04-62.976 0-88.064 25.6-27.648 69.632-27.648 95.232 0l204.8 222.208c23.04 24.576 23.04 62.976 0 87.552l-204.8 222.208c-25.6 27.648-69.12 28.16-94.72 0.512z" p-id="11604"/>
                          <title>Previous change/break point</title>
                        </g>
                      </svg>
                    </g>
                    <g v-if="item.isFixHighlight && item.isEqNext"
                       class="param-item-link-right"
                       :transform="`translate(${[item.x + item.width - navIconSize / 2, item.y + item.height / 2 - navIconSize / 2]})`">
                      <svg t="1710230334748" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="11603" xmlns:xlink="http://www.w3.org/1999/xlink" :width="navIconSize" :height="navIconSize">
                        <g @click="clickParamRectRight(item)">
                          <circle cx="512" cy="512" r="400" fill="white" p-id="11604"></circle>
                          <path :fill="getItemColor(item)"
                                d="M512 43.52c-258.56 0-468.48 209.92-468.48 468.48s209.92 468.48 468.48 468.48 468.48-209.92 468.48-468.48-209.92-468.48-468.48-468.48zM398.336 783.36c-23.04-24.576-23.04-62.976 0-88.064l123.904-134.144c23.04-24.576 23.04-62.976 0-87.552L397.824 338.944c-23.04-24.576-23.04-62.976 0-88.064 25.6-27.648 69.632-27.648 95.232 0l204.8 222.208c23.04 24.576 23.04 62.976 0 87.552l-204.8 222.208c-25.6 27.648-69.12 28.16-94.72 0.512z" p-id="11604"/>
                          <title>Next change/break point</title>
                        </g>
                      </svg>
                    </g>
                    <g v-if="item.fixed"
                       style="pointer-events: none;"
                       :transform="`translate(${[item.x + item.width / 2 - 11, item.y - 11]})`">
                      <svg t="1710227415094" class="icon" viewBox="0 0 1025 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1464" xmlns:xlink="http://www.w3.org/1999/xlink" width=22 height="22">
                        <circle cx="512" cy="512" r="250" fill="white" p-id="11604"></circle>
                        <path :fill="getItemColor(item)"
                              d="M511.999 225.386C177.707 225.386 2.441 472.773 2.441 512c0 39.226 175.264 286.614 509.558 286.614 334.273 0 509.558-247.388 509.558-286.614 0-39.227-175.285-286.614-509.558-286.614z m0 507.089c-125.087 0-226.477-98.71-226.477-220.475 0-121.787 101.39-220.475 226.477-220.475 125.088 0 226.477 98.69 226.477 220.475 0 121.765-101.39 220.475-226.477 220.475z m0-220.475c-20.754-22.889 33.796-110.258 0-110.258-62.554 0-113.228 49.387-113.228 110.258 0 60.871 50.673 110.217 113.228 110.217 62.513 0 113.23-49.345 113.23-110.217 0-27.989-95.585 19.427-113.23 0z" p-id="19679"></path>
                      </svg>
                    </g>
                  </g>
                </g>
              </g>
            </g>

<!--            <g class="icon-group" v-show="showEvoLabel">-->
<!--              <g v-if="node.isAdded()"-->
<!--                 :transform="`translate(${[-iconSize/2, (node.height - iconSize)/2]})`">-->
<!--                <svg t="1687245465763" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9614" :width="iconSize" :height="iconSize">-->
<!--                  <circle :cx="1024 / 2" :cy="1024 / 2" :r="1024 * 0.3" fill="white"/>-->
<!--                  <path :fill="'#5dbb54'" d="M512 64C213.3 64 64 213.3 64 512s149.3 448 448 448 448-149.3 448-448S810.7 64 512 64z m224.2 513.3H577.7v158.5c0 31.8-25.8 57.6-57.6 57.6s-57.6-25.8-57.6-57.6V577.3H303.9c-31.8 0-57.6-25.8-57.6-57.7 0-31.8 25.8-57.6 57.6-57.6h158.5V303.5c0-31.9 25.8-57.6 57.6-57.6s57.6 25.7 57.6 57.6V462h158.5c31.8 0 57.6 25.8 57.6 57.6 0.2 31.9-25.6 57.7-57.5 57.7z" p-id="9615"></path></svg>-->
<!--              </g>-->
<!--              <g v-if="node.toRemove()"-->
<!--                 :transform="`translate(${[node.width - iconSize/2, (node.height - iconSize)/2]})`">-->
<!--                <svg t="1687245508476" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9759" :width="iconSize" :height="iconSize">-->
<!--                  <circle :cx="1024 / 2" :cy="1024 / 2" :r="1024 * 0.3" fill="white"/>-->
<!--                  <path :fill="'#ff5454'" d="M512 64C213.3 64 64 213.3 64 512s149.3 448 448 448 448-149.3 448-448S810.7 64 512 64z m224.2 513.3H303.9c-31.8 0-57.6-25.8-57.6-57.7 0-31.8 25.8-57.6 57.6-57.6h432.4c31.8 0 57.6 25.8 57.6 57.6 0 31.9-25.8 57.7-57.7 57.7z" p-id="9760"></path></svg>-->
<!--              </g>-->
<!--            </g>-->
          </g>
        </g>
      </g>
    </g>
  </g>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {getEvoTypeColor, getFadedColor} from "@/js/common"
import {getLimitedString, getTextSize} from "@/utils/Layout"
import {VisTraceTree} from "@/js/trace/VisTraceTree"

export default {
  name: 'PlanView',
  components: {
  },
  props: {
    visTraceTree: VisTraceTree,
  },
  data() {
    return {
    }
  },
  mounted() {
    this.svgEl = this.$refs.svg
  },
  methods: {
    ...mapMutations('trace', [
        'changeFixHighlightObject',
        'scrollToItemAndHighlight',
    ]),
    clickSvg() {
    },
    clickAction(act) {
      console.log(act)
    },
    clickPlan(visPlan, i) {
      const indexInPlans = this.visTraceTree.origin.trace.plans.indexOf(visPlan.origin)
      console.log(indexInPlans, visPlan.origin)
    },
    clickNode(node) {
      console.log(node.toString())
      console.log(node)
    },
    clickEdge(edge) {
      console.log(edge.toString())
    },
    getNodeNameWithId(visPlanNode) {
      const {useOptAlias} = this.configV3
      const {nodeWidth, fontSize, idScale} = this.configV3.plan

      const id = visPlanNode.getNodeId()
      const {width: idWidth} = getTextSize('#' + id, fontSize * idScale)

      let name = visPlanNode.getNodeName()
      if (useOptAlias) {
        name = this.optInfoMap.get(visPlanNode.planNode.name)?.alias ?? '?'
      }
      name = getLimitedString(name, nodeWidth - idWidth, fontSize)

      return name
    },
    getNodeName(visPlanNode) {
      const {useOptAlias} = this.configV3
      const {nodeWidth, fontSize} = this.configV3.plan

      let name = visPlanNode.getNodeName()
      if (useOptAlias) {
        name = this.optInfoMap.get(visPlanNode.planNode.name)?.alias ?? '?'
      }
      name = getLimitedString(name, nodeWidth, fontSize)

      return name
    },
    getNodeId(visPlanNode) {
      return visPlanNode.getNodeId()
    },
    getEvoFill(type) {
      switch (type) {
        case 'A': return 'url(#gradient-add)'
        case 'R': return 'url(#gradient-remove)'
        case 'AR': return 'url(#gradient-add-remove)'
        case 'U': return getEvoTypeColor('U')
      }
      return 'red'
    },
    getEvoTypeColor(type) {
      return getEvoTypeColor(type)
    },
    getMetaTypeColor(type) {
      return getFadedColor(type)
    },
    getLimitedString(str, width, fontSize) {
      return getLimitedString(str, width, fontSize)
    },
    getLimitedParamStrings(node) {
      const strings = node.origin.paramArray
      // limit size to 8. add '...' if truncated
      const maxLen = 8
      const limitedStrings = strings.slice(0, maxLen)
      if (strings.length > maxLen) {
        limitedStrings.push('...')
      }
      return limitedStrings
    },
    /**
     * @param {VisQueryPlan} plan
     * @param {VisParamItem} item
     */
    enterParamRect(plan, item) {
      if (!this.transSupportEnabled) { return }
      item.highlight()
    },
    /**
     * @param {VisQueryPlan} plan
     * @param {VisParamItem} item
     */
    leaveParamRect(plan, item) {
      const doLeaveParamRect = () => {
        if (!this.transSupportEnabled) { return }
        item.unhighlight()
      }
      if (this.hoverDelay) {
        setTimeout(doLeaveParamRect, 2000)
      } else {
        doLeaveParamRect()
      }
    },
    /**
     * @param {VisParamItem} item
     */
    clickParamRect(item) {
      if (!this.transSupportEnabled) { return }
      if (item.fixed) {
        this.changeFixHighlightObject(null)
      } else {
        this.changeFixHighlightObject(item)
      }
    },
    getItemColor(item) {
      if (item.isHighlight) {
        return this.color.highlight
      }
      if (item.isFixHighlight) {
        return this.color.fixHighlight
      }
      return this.color.normal
    },
    clickParamRectLeft(item) {
      const prev = item.getPrevChItem()
      // this.changeFixHighlightItem(prev)
      const itemEl = document.getElementById('p' + prev.id)
      this.scrollToItemAndHighlight({vItem: prev, itemEl})
    },
    clickParamRectRight(item) {
      const next = item.getNextChItem()
      // this.changeFixHighlightItem(next)
      const itemEl = document.getElementById('p' + next.id)
      this.scrollToItemAndHighlight({vItem: next, itemEl})
    },
  },
  watch: {
  },
  computed: {
    ...mapState('trace', {
      configV1: state => state.configV1,
      configV3: state => state.configV3,
      color: state => state.configV3.color,
      navIconSize: state => state.configV3.plan.navIconSize,
      planPadding: state => state.configV3.plan.padding,
      fontSize: state => state.configV3.plan.fontSize,
      edgeFontSize: state => state.configV3.plan.edgeFontSize,
      idScale: state => state.configV3.plan.idScale,
      iconSize: state => state.configV3.plan.iconSize,
      nodeTitleHeight: state => state.configV3.plan.nodeTitleHeight,
      paramRowHeight: state => state.configV3.plan.paramRowHeight,
      paramFontSize: state => state.configV3.plan.paramFontSize,
      paramItemMargin: state => state.configV3.plan.paramItemMargin,
      showEvoLabel: state => state.showEvoLabel,
      transSupportEnabled: state => state.transSupportEnabled,
      hoverDelay: state => state.hoverDelay,
    }),
    width() {
      return this.visTraceTree?.width ?? 0
    },
    height() {
      return this.visTraceTree?.height ?? 0
    },
    treeRoot() {
      return this.visTraceTree?.root ?? null
    },
  }
}
</script>

<style scoped>
.trace-plan-view {
  padding: 10px;

  display: flex;
  overflow: auto;
}
.plan-item {
  flex-shrink: 0;
}
.node-label {
  user-select: none;
  font-weight: bold;
}
.params {
  user-select: none;
}
.param-item-rect-group {
  cursor: pointer;
}
.param-item-link-left {
  cursor: w-resize;
}
.param-item-link-right {
  cursor: e-resize;
}
</style>
