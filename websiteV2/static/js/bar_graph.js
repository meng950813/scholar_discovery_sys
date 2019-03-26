/**
 * author: dong, xiaoniu
 * date: 2019-03-26
 */
class VerticalBarGraph{
    /**
     * 构造函数
     * @param svg 图标所需要的画布svg,其属性必须包含width和height两个参数
     * @param xTexts x轴显示的内容
     */
    constructor(svg, xTexts){
        this.svg = svg;
        //获取宽度和高度
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        //所有的控件都在同一个group中
        this.group = this.svg.append('g');
        //画布周边的空白
        this.margin = {left:30, right:30, top:20, bottom:20};
        //x轴的比例尺
        this.xScale = d3.scaleBand()
            .domain(d3.range(xTexts.length))
            .rangeRound([0, this.width - this.margin.left - this.margin.right]);
        //y轴的比例尺
        this.yScale = d3.scaleLinear()
            .domain([0, 20])
            .range([this.height - this.margin.top - this.margin.bottom, 0]);
        //文字比例尺
        this.tScale = d3.scaleBand()
            .domain(xTexts)
            .rangeRound([0, this.width - this.margin.left - this.margin.right]);
        //定义x轴
        this.xAxis = d3.axisBottom()
            .scale(this.tScale);
        //定义y轴
        this.yAxis = d3.axisLeft()
            .scale(this.yScale);
        //添加x轴
        this.group.append("g")
            .attr("class","axis")
            .attr("transform","translate(" + this.margin.left + "," + (this.height - this.margin.bottom) + ")")
            .call(this.xAxis);
        //添加y轴
        this.group.append("g")
            .attr("class","axis")
            .attr('id', 'yAxis')
            .attr("transform","translate(" + this.margin.left + "," + this.margin.top + ")")
            .call(this.yAxis);
        //矩形
        this.group.append('g')
            .attr('id', 'rects');
    }

    setData(dataset){
        //更改y轴
        this.yScale.domain([0, d3.max(dataset)]);
        this.yAxis.scale(this.yScale);
        this.group.select('#yAxis').call(this.yAxis);
        //清除原先的数据
        this.group.select('#rects').selectAll('g').remove();
        //矩形之间的空白
        let rectPadding = 30;
        let group = this.group.select('#rects')
            .selectAll('g')
            .data(dataset)
            .enter()
            .append('g');
        let that = this;
        //添加矩形
        group.append('rect')
            .attr('fill', '#ffcc62')
            .attr("transform","translate(" + that.margin.left + "," + that.margin.top + ")")
            .attr("x", function(d,i){
                return that.xScale(i) + rectPadding/2;
            })
            .attr("y",d => that.yScale(d))
            .attr("width", that.xScale.bandwidth() - rectPadding )
            .attr("height", function(d){
                return that.height - that.margin.top - that.margin.bottom - that.yScale(d);
            });
        //添加文字
        let fontSize = 1;
        group.append('text')
            .attr("transform","translate(" + this.margin.left + "," + this.margin.top + ")")
            .attr("x", function(d,i){
                return that.xScale(i) + rectPadding/2;
            } )
            .attr("y",function(d){
                return that.yScale(d) - 25;
            })
            .attr("dx",function(d){
                let len = String(d);
                return (that.xScale.bandwidth() - rectPadding - fontSize * len)/2;
            })
            .attr("dy",20)
            .text(d => d);
    }
}