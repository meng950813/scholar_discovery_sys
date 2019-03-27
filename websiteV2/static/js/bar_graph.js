/**
 * author: dong, xiaoniu
 * date: 2019-03-26
 */
/**
 * 竖柱形图
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
        //画布周边的空白
        this.margin = {left:30, right:30, top:20, bottom:20};
        //所有的控件都在同一个group中
        this.group = this.svg.append('g');
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
        //矩形都添加在此矩形
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
        let fontSize = 5;
        group.append('text')
            .attr("transform","translate(" + this.margin.left + "," + this.margin.top + ")")
            .attr("x", function(d,i){
                return that.xScale(i) + rectPadding/2 - 4;
            } )
            .attr("y",function(d){
                return that.yScale(d) - 25;
            })
            .attr("dx",function(d){
                let len = String(d).length;
                return (that.xScale.bandwidth() - rectPadding - fontSize * len)/2;
            })
            .attr("dy",20)
            .text(d => d);
    }
}

/**
 * 横柱形图
 */
class HorizontalBarGraph{
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
        //画布周边的空白
        this.margin = {left:120, right:80, top:80, bottom:40};
        //所有的控件都在同一个group中
        this.group = this.svg.append('g')
            .attr("transform","translate(" + this.margin.left + "," + this.margin.top + ")");
        //x轴的比例尺
        this.xScale = d3.scaleLinear()
            .domain([0, 20])
            .range([0, this.width - this.margin.left - this.margin.right]);
        //y轴的比例尺
        this.yScale = d3.scaleBand()
            .domain(d3.range(xTexts.length))
            .rangeRound([0, this.height - this.margin.top - this.margin.bottom]);
        //文字比例尺
        this.tScale = d3.scaleBand()
            .domain(xTexts)
            .rangeRound([0, this.height - this.margin.top - this.margin.bottom]);
        //定义x轴
        this.xAxis = d3.axisTop()
            .scale(this.xScale);
        //定义y轴
        this.yAxis = d3.axisLeft()
            .scale(this.tScale);
        //添加x轴
        this.group.append("g")
            .attr("class","axis")
            .attr('id', 'xAxis')
            .call(this.xAxis);
        //添加y轴
        this.group.append("g")
            .attr("class","axis")
            .attr('id', 'yAxis')
            .call(this.yAxis);
        //更改文本显示大小
        this.group.select('#yAxis').attr('font-size', '14');
        //矩形
        this.group.append('g')
            .attr('id', 'rects');
    }

    setData(json_data){
        let dataset = json_data['dataset'];
        let categories = json_data['categories'];
        let length = categories.length;
        //更改x轴的映射
        this.xScale.domain([0, d3.max(dataset)]);
        this.xAxis.scale(this.xScale);
        this.group.select('#xAxis').call(this.xAxis);
        //更改y轴的映射
        this.yScale.domain(d3.range(dataset.length));
        //生成提示
        this.updateCategories(categories);
        //清除原先的数据
        this.group.select('#rects').selectAll('g').remove();
        //矩形之间的空白
        let rectPadding = this.yScale(1);
        let group = this.group.select('#rects')
            .selectAll('g')
            .data(dataset)
            .enter()
            .append('g');
        let that = this;
        //添加矩形
        group.append('rect')
            .attr('fill', (d, i) => categories[i % length].color)
            .attr("x", 1)
            .attr("y",(d, i) => that.yScale(i) + rectPadding / 6 * (3 - i % length))
            .attr("width", d => that.xScale(d))
            .attr("height", function(d){
                return that.yScale.bandwidth() / 2;
            });
        //添加文字
        let fontSize = 5;
        group.append('text')
            .attr("x", function(d,i){
                return that.xScale(d);
            } )
            .attr("y",function(d, i){
                return that.yScale(i) + rectPadding / 6 * (3 - i % length);
            })
            .attr("dx",function(d){
                return 20;
            })
            .attr('dy', rectPadding / 3)
            .text(d => d);
    }

    updateCategories(categories){
        if (this.categories_group == null){
            this.categories_group = this.svg
                .append('g')
                .attr('id', 'categories')
                .attr('transform', 'translate(' + this.margin.left + ',' + 0 + ')');
        }
        let that = this;
        //先移除原先的类别
        this.categories_group.selectAll('g').remove();

        let group = this.categories_group.selectAll('g')
            .data(categories)
            .enter()
            .append('g')
            .attr('cursor', 'pointer');
        //添加
        let width = 0;
        let fontWidth = 17;
        //矩形宽度
        let rectWidth = 30;
        //添加矩形
        group.append('rect')
            .attr('x', function (d, i) {
                d.status = true;
                if (i > 0)
                    width += categories[i - 1].name.length * fontWidth;
                return i * rectWidth + width;
            })
            .attr('y', 20)
            .attr('fill', d => d.color)
            .attr('width', rectWidth)
            .attr('height', 15)
            .attr('rx', 5)
            .attr('ry', 5);
        //添加文本
        width = 0;
        group.append('text')
            .attr('x', function (d, i) {
                if (i > 0)
                    width += categories[i - 1].name.length * fontWidth;
                return (i + 1) * rectWidth + width;
            })
            .attr('y', 32)
            .text(d => d.name)
            .attr('fill', (d) => d.color);
        // //添加可点击函数
        // group.on('click', function (datum, index) {
        //     that.clickCategoryCallback(datum, index);
        // });
    }
}
