/**
 * author: sky
 * date: 2019-03-29
 * 折线图/区域图
 */
class AreaChart{
    constructor(svg){
        this.svg = svg;
        //获取宽度和高度
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        //画布周边的空白
        this.margin = {left:20, right:0, top:20, bottom:20};
        //所有的控件都在同一个group中
        this.group = this.svg.append('g');
        //x轴的比例尺
        this.xScale = d3.scalePoint()
            .domain(d3.range(10))
            .range([0, this.width - this.margin.left - this.margin.right]);
        //y轴的比例尺
        this.yScale = d3.scalePoint()
            .domain(d3.range(4))
            .range([this.height - this.margin.top - this.margin.bottom, 0]);
        //定义x轴
        this.xAxis = d3.axisBottom()
            .scale(this.xScale);
        //定义y轴
        this.yAxis = d3.axisLeft()
            .scale(this.yScale);
        //矩形都添加在此group中
        this.group.append('g')
            .attr('id', 'chart');
        //添加x轴
        this.group.append("g")
            .attr("class","axis")
            .attr('id', 'xAxis')
            .attr("transform","translate(" + this.margin.left + "," + (this.height - this.margin.bottom) + ")")
            .call(this.xAxis);
        //添加y轴
        this.group.append("g")
            .attr("class","axis")
            .attr('id', 'yAxis')
            .attr("transform","translate(" + this.margin.left + "," + this.margin.top + ")")
            .call(this.yAxis);
    }
    setData(data){
        //更改x轴
        let xData = data.map((item) => item.name);
        this.xScale.domain(xData)
            .range([0, this.width - this.margin.left - this.margin.right - 50]);
        this.xAxis.scale(this.xScale);
        this.group.select('#xAxis').call(this.xAxis);
        //更改y轴
        let yData = data.map((item) => item.value);
        yData.push(0);
        this.yScale.domain(yData.sort((a, b) => a - b));
        this.yAxis.scale(this.yScale);
        this.group.select('#yAxis').call(this.yAxis);
        let that = this;
        //创建一个区域生成器
        let area = d3.area()
            .x(function (d, i) {
                return that.xScale(d.name) + that.margin.left;
            })
            .y0(function (d, i) {
                return that.height - that.margin.bottom;
            })
            .y1(function (d, i) {
                return that.yScale(d.value) + that.margin.top;
            })
            .curve(d3.curveCatmullRom);
        //添加样式
        this.group.select('#chart')
            .append('path')
            .attr('d', area(data))
            .style('fill', '#ffdec8');
        //创建线条
        let line = d3.line()
            .x(function (d, i) {
                return that.margin.left + that.xScale(d.name);
            })
            .y(function (d, i) {
                return that.yScale(d.value) + that.margin.top;
            })
            .curve(d3.curveCatmullRom);
        //添加线条
        this.group.select('#chart').append('path')
            .attr('stroke', '#ff8838')
            .attr('stroke-width', '3px')
            .attr('fill', 'none')
            .attr('class', 'line')
            .attr('d', line(data));
        //添加circle描述
        let circle = this.group.select('#chart').selectAll('circle')
            .data(data)
            .enter()
            .append('circle')
            .style('fill', 'white')
            .style('stroke', '#ff8838')
            .style('stroke-width', '2')
            .attr('r', 3)
            .attr('cx', function (d, i) {
                return that.margin.left + that.xScale(d.name);
            })
            .attr('cy', function (d) {
                return that.yScale(d.value) + that.margin.top;
            });
    }
}
