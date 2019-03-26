/**
 * author: xiaoniu
 * date: 2019-03-18
 * 包含了通用的一些函数
 */
/**
 * 设置动画显示/隐藏提示面板
 * @param tooltip 面板元素
 * @param {boolean} visible 显示/隐藏 为true时会更新提示面板位置，为false会隐藏面板
 * @param  html 只有visible为true时才会更新面板显示
 */
function setVisibleOfToolTip(tooltip, visible, html = null){
    let duration = null, opacity = null;
    //渐渐显示tooltip
    if (visible){
        tooltip.style('left', (d3.event.pageX) + 'px').style('top', (d3.event.pageY - 28) + 'px');
        //设置文本
        if (html != null){
            tooltip.html(html);
            duration = 200;opacity = 0.8;
        }
    }
    //动画隐藏提示框
    else{
        duration = 500;
        opacity = 0;
    }
    if (duration != null && opacity != null){
        tooltip.transition().duration(duration).style('opacity', opacity);
    }
}
