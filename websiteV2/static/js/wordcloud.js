/**
 * author: xiaoniu
 * date: 2019-03-19
 * desc: 显示词云的类，依赖于d3.js
 */

 /**
 * 自执行函数，用于设置 词云 + 关系图 + 的宽高
 */
(function(){
    let width = $(".container").width();
    let height = parseInt( width / 2 );

    if(width > 900){
        height = parseInt( width / 3 );
    }

    $("#word-cloud").attr("width", width).attr("height" , height);
    
    $("#relation-net").attr("width", width).attr("height" , height);

    if(width > 720 ){
        width = width / 2;
    }
    $("#paper-chart").attr("width", width).attr("height" , height / 2);

    $("#cited-chart").attr("width", width).attr("height" , height / 2);
    
})();






class WordCloud{
    constructor(svg){
        this.svg = svg;
        this.width = this.svg.attr('width');
        this.height = this.svg.attr('height');
        //添加group元素
        this.group = this.svg.append('g')
            .attr('transform', 'translate(' + this.width / 2 + ',' + this.height / 2 + ')');

        this.colors = d3.schemeCategory10;
        this.layout = d3.layout.cloud()
            .size([this.width, this.height])
            .padding(5)
            .rotate(0)
            //.rotate(() => ~~(Math.random() * 2) * 90)
            .font('Impact');
    }

    /**
     * 设置数据，并显示
     * @param words 数据格式如{text: 护理, size:20}
     */
    setData(words){
        let that = this;
        this.layout.words(words)
            .fontSize(d => d.size)
            .on('end', function (d) {
               that.draw(d);
            });
        //启动布局算法
        this.layout.start();
    }
    draw(words) {
        this.group.selectAll('text')
            .data(words)
            .enter()
            .append('text')
            .style('font-size', d => d.size + 'px')
            .style('font-family', 'Impact')
            .style('fill', (d, i) => this.colors[Math.floor(Math.random() * 10)])
            .attr('text-anchor', 'middle')
            .attr('transform', d => 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')')
            .text(d => d.text);
    }
}